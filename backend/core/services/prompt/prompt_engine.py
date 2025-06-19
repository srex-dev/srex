# backend/core/services/prompt/prompt_engine.py

import re
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from jinja2 import Template, FileSystemLoader, Environment
from llm.interface import call_llm
from backend.core.logger import logger
# from backend.core.basic_validator import basic_output_shape_check
# TODO: Update to correct import path or implement basic_output_shape_check if needed
from core.config import CONFIG
from backend.core.domain.metrics.loader import load_metrics_adapter

from backend.core.output_schema import validate_srex_output

def basic_output_shape_check(data, required_keys):
    # TODO: Implement real validation
    return []

class TemplateManager:
    def __init__(self, template_dir: str = "llm/prompt_templates"):
        self.template_dir = Path(template_dir)
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))

    def get_template_path(self, template: str) -> Path:
        template_path = Path(template) if Path(template).is_file() else self.template_dir / f"{template}.j2"
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        return template_path

    def render_template(self, template: str, context: Dict[str, Any]) -> str:
        template_path = self.get_template_path(template)
        template_content = template_path.read_text()
        return Template(template_content).render(**context)

    def render_sli_fields(self, sli_inputs: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        for sli in sli_inputs:
            for field in ["query", "name", "description", "metric", "source"]:
                if field in sli and isinstance(sli[field], str) and "{{" in sli[field]:
                    try:
                        sli[field] = Template(sli[field]).render(**context)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to render {field} for {sli.get('name', 'unknown')}: {e}")
        return sli_inputs


def remove_trailing_commas(json_str: str) -> str:
    # Remove trailing commas before } or ]
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    return json_str

def dicts_with_numeric_keys_to_lists(obj):
    """Convert dicts with only numeric keys to lists."""
    if isinstance(obj, dict):
        # If all keys are numeric, convert to list
        if all(str(k).isdigit() for k in obj.keys()) and obj:
            # Sort keys numerically and convert to list
            sorted_keys = sorted(obj.keys(), key=lambda x: int(x))
            result = [dicts_with_numeric_keys_to_lists(obj[k]) for k in sorted_keys]
            return result
        else:
            # Recursively process all values
            return {k: dicts_with_numeric_keys_to_lists(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [dicts_with_numeric_keys_to_lists(v) for v in obj]
    else:
        return obj

def convert_types_for_schema(data):
    """Convert data types to match schema expectations."""
    if isinstance(data, dict):
        return {k: convert_types_for_schema(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_types_for_schema(v) for v in data]
    elif isinstance(data, str):
        # Try to convert string to number if it looks like a number
        try:
            if '.' in data:
                return float(data)
            else:
                return int(data)
        except (ValueError, TypeError):
            return data
    else:
        return data

class ResponseProcessor:
    def __init__(self, model: str, temperature: float, step_name: str = "unknown", input_context: Dict[str, Any] = None):
        self.model = model
        self.temperature = temperature
        self.step_name = step_name
        self.input_context = input_context or {}

    def process_response(self, raw_output: str, explain: bool) -> Dict[str, Any]:
        try:
            cleaned_output = remove_trailing_commas(raw_output)
            json_data = self._extract_json_block(cleaned_output)
        except ValueError as e:
            logger.warning(f"⚠️ First parse failed: {e}")
            retry_prompt = raw_output + "\n\n🔁 Retry: Return ONLY a valid JSON object with no explanation."
            raw_output = call_llm(retry_prompt, explain=False, model=self.model, temperature=self.temperature)
            cleaned_output = remove_trailing_commas(raw_output)
            json_data = self._extract_json_block(cleaned_output)

        if explain and not json_data.get("explanation"):
            logger.warning("⚠️ Missing 'explanation' in JSON. Attempting extraction from raw output.")
            json_data["explanation"] = self._extract_explanation_block(raw_output).strip()

        # Save original for debugging
        Path("debug/original_json.json").write_text(json.dumps(json_data, indent=2))

        # Convert dicts with numeric keys to lists
        json_data = dicts_with_numeric_keys_to_lists(json_data)
        
        # Save after numeric key conversion for debugging
        Path("debug/after_numeric_conversion.json").write_text(json.dumps(json_data, indent=2))

        self._ensure_required_keys(json_data, raw_output)
        self._clean_placeholders(json_data)
        self._add_metadata(json_data)
        self._calculate_confidence(json_data)

        # Post-process output for all templates
        json_data = self.clean_llm_output(json_data)
        
        # Convert types for schema validation
        json_data = convert_types_for_schema(json_data)
        
        # Save final data for debugging
        Path("debug/final_json.json").write_text(json.dumps(json_data, indent=2))

        # Save the exact data being validated
        Path(f"debug/data_for_validation_{self.step_name}.json").write_text(json.dumps(json_data, indent=2))
        logger.info(f"🔍 Validating data for {self.step_name} with keys: {list(json_data.keys())}")

        # Use appropriate schema type based on step name
        schema_type = "drift_suggestions" if self.step_name in ["drift_suggestions", "scorecard_suggestions"] else "slo"
        is_valid, errors = validate_srex_output(json_data, schema_type=schema_type)
        if not is_valid:
            logger.warning(f"⚠️ Output structure issues in {self.step_name}:\n" + json.dumps(errors, indent=2))
            # Save the problematic data for debugging
            Path(f"debug/validation_error_{self.step_name}.json").write_text(json.dumps(json_data, indent=2))

        return json_data

    def _extract_json_block(self, text: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM output with enhanced error handling."""
        # First, try to parse as JSON directly
        try:
            # logger.debug(f"🔍 Trying direct JSON parse for {self.step_name}")
            result = json.loads(text)
            # logger.debug(f"✅ Direct JSON parse successful for {self.step_name}")
            return result
        except Exception as e:
            # logger.debug(f"❌ Direct JSON parse failed for {self.step_name}: {e}")
            pass  # Fall through to cleaning

        try:
            # Clean the text first
            cleaned = text.strip()
            # logger.debug(f"🔍 Extracting JSON block for {self.step_name}, text length: {len(cleaned)}")
            
            # Check if the response is conversational instead of JSON
            conversational_indicators = [
                "hello", "hi", "how can i help", "what would you like", 
                "is there something", "can i help you", "let me help",
                "i'd be happy to help", "sure", "absolutely", "of course"
            ]
            
            cleaned_lower = cleaned.lower()
            # Only check for conversational indicators if the response doesn't start with JSON
            if not (cleaned.strip().startswith("{") or cleaned.strip().startswith("[")):
                if any(indicator in cleaned_lower for indicator in conversational_indicators):
                    logger.warning(f"⚠️ LLM returned conversational response instead of JSON for {self.step_name}")
                    logger.warning(f"⚠️ Raw response: {cleaned[:200]}...")
                    return self._get_default_response()
            else:
                logger.info("✅ Response appears to be valid JSON, skipping conversational check")
            
            # Find the first { and last }
            start = cleaned.find('{')
            if start == -1:
                logger.warning(f"❌ No opening brace found for {self.step_name}")
                logger.warning(f"⚠️ Raw response: {cleaned[:200]}...")
                return self._get_default_response()
            
            # Count braces to find the matching end
            brace_count = 0
            end = -1
            for i, char in enumerate(cleaned[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i
                        break
            
            if end == -1 or end <= start:
                # Unmatched braces, try multiple fixing strategies
                logger.warning(f"⚠️ Unmatched braces in JSON for {self.step_name}, attempting to fix")
                
                # Strategy 1: Find the last complete object
                last_brace = cleaned.rfind('}')
                if last_brace > start:
                    json_str = cleaned[start:last_brace + 1]
                else:
                    # Strategy 2: Try to balance braces by adding missing ones
                    open_braces = cleaned.count('{')
                    close_braces = cleaned.count('}')
                    if open_braces > close_braces:
                        # Add missing closing braces
                        json_str = cleaned[start:] + '}' * (open_braces - close_braces)
                    elif close_braces > open_braces:
                        # Find the last valid position to add opening braces
                        json_str = cleaned[start:last_brace + 1]
                    else:
                        logger.warning(f"❌ Could not fix JSON structure for {self.step_name}")
                        logger.warning(f"⚠️ Raw response: {cleaned[:200]}...")
                        return self._get_default_response()
            else:
                json_str = cleaned[start:end + 1]
            
            # Try to parse the extracted JSON
            try:
                result = json.loads(json_str)
                return result
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ JSON decode error for {self.step_name}: {e}")
                logger.warning(f"⚠️ Attempted to parse: {json_str[:200]}...")
                
                # Try to fix common JSON issues
                fixed_json = self._fix_common_json_issues(json_str)
                try:
                    result = json.loads(fixed_json)
                    logger.info(f"✅ Successfully fixed JSON for {self.step_name}")
                    return result
                except json.JSONDecodeError:
                    logger.warning(f"❌ Could not fix JSON for {self.step_name}")
                    return self._get_default_response()
                    
        except Exception as e:
            logger.error(f"❌ Unexpected error extracting JSON for {self.step_name}: {e}")
            logger.warning(f"⚠️ Raw response: {text[:200]}...")
            return self._get_default_response()

    def _fix_common_json_issues(self, json_str: str) -> str:
        """Fix common JSON formatting issues."""
        # Remove trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix missing quotes around property names
        json_str = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2"\3:', json_str)
        
        # Fix missing quotes around string values
        json_str = re.sub(r':\s*([^"][^,}\]]*[^"\s,}\]])', r': "\1"', json_str)
        
        # Fix unescaped quotes in strings
        json_str = re.sub(r'([^\\])"([^"]*?)([^\\])"', r'\1"\2\3"', json_str)
        
        return json_str

    def _get_default_response(self) -> Dict[str, Any]:
        """Return a default response structure when JSON parsing fails, respecting quantity controls."""
        # Special handling for drift suggestions
        if self.step_name == "drift_suggestions":
            return {
                "ai_confidence": 0.0,
                "priority_actions": [
                    "Review drift metrics for concerning trends",
                    "Focus on the most declining metric first",
                    "Implement monitoring for drift tracking"
                ],
                "improvement_areas": ["Overall system stability"],
                "suggestions": [
                    "Analyze the drift breakdown to identify specific issues",
                    "Set up alerts for when drift exceeds thresholds",
                    "Create action plans for each drift area"
                ],
                "root_causes": ["Insufficient data for detailed analysis"],
                "success_metrics": [
                    "Reduction in drift magnitude",
                    "Stabilization of key metrics",
                    "Improved consistency over time"
                ],
                "explanation": f"Unable to parse LLM response for {self.step_name}. Please check the debug logs."
            }
        
        # Special handling for scorecard suggestions
        if self.step_name == "scorecard_suggestions":
            return {
                "ai_confidence": 0.0,
                "priority_actions": [
                    "Review scorecard metrics for improvement opportunities",
                    "Focus on the lowest scoring areas first",
                    "Implement monitoring for scorecard tracking"
                ],
                "improvement_areas": ["Overall system performance"],
                "suggestions": [
                    "Analyze the scorecard breakdown to identify specific issues",
                    "Set up alerts for when scores fall below thresholds",
                    "Create action plans for each scorecard area"
                ],
                "root_causes": ["Insufficient data for detailed analysis"],
                "success_metrics": [
                    "Improvement in scorecard scores",
                    "Stabilization of key metrics",
                    "Enhanced system performance over time"
                ],
                "explanation": f"Unable to parse LLM response for {self.step_name}. Please check the debug logs."
            }
        
        # Get quantity controls from input context
        sli_quantity = self.input_context.get("sli_quantity", 5)
        slo_quantity = self.input_context.get("slo_quantity", 3)
        alert_quantity = self.input_context.get("alert_quantity", 3)
        suggestion_quantity = self.input_context.get("suggestion_quantity", 5)
        
        # Generate appropriate number of default items based on step and quantities
        if "sli" in self.step_name.lower():
            sli_items = [{"name": f"Default SLI {i+1}", "description": f"Auto-generated SLI {i+1}", "type": "custom", "unit": "", "source": "prometheus", "metric": ""} for i in range(min(sli_quantity, 3))]
        else:
            sli_items = []
            
        if "slo" in self.step_name.lower():
            slo_items = [{"name": f"Default SLO {i+1}", "description": f"Auto-generated SLO {i+1}", "sli": "default_sli", "target": 99.0, "time_window": "30d"} for i in range(min(slo_quantity, 3))]
        else:
            slo_items = []
            
        if "alert" in self.step_name.lower():
            alert_items = [{"name": f"Default Alert {i+1}", "description": f"Auto-generated alert {i+1}", "severity": "warning", "expr": "", "for": "5m"} for i in range(min(alert_quantity, 3))]
        else:
            alert_items = []
            
        if "suggestion" in self.step_name.lower() or "recommendation" in self.step_name.lower():
            suggestion_items = [{"metric": f"metric_{i+1}", "recommendation": f"Auto-generated recommendation {i+1}"} for i in range(min(suggestion_quantity, 3))]
        else:
            suggestion_items = ["Review the LLM response format and ensure valid JSON is generated."]
        
        return {
            "sli": sli_items,
            "slo": slo_items,
            "alerts": alert_items,
            "explanation": f"Unable to parse LLM response for {self.step_name}. Please check the debug logs.",
            "llm_suggestions": suggestion_items
        }

    def _extract_explanation_block(self, text: str) -> str:
        try:
            start = text.find('{')
            end = text.rfind('}')
            if start == -1 or end == -1:
                return ""
            json_str = text[start:end + 1]
            parsed = json.loads(json_str)
            return parsed.get("explanation", "").strip()
        except Exception:
            return ""

    def _ensure_required_keys(self, json_data: Dict[str, Any], raw_output: str) -> None:
        # Special handling for drift suggestions
        if self.step_name == "drift_suggestions":
            required_keys = ["ai_confidence", "priority_actions", "improvement_areas", "suggestions", "root_causes", "success_metrics", "explanation"]
            for key in required_keys:
                if key not in json_data:
                    if key == "explanation":
                        json_data[key] = self._extract_explanation_block(raw_output)
                    elif key == "ai_confidence":
                        json_data[key] = 0.0
                    elif key in ["priority_actions", "improvement_areas", "suggestions", "root_causes", "success_metrics"]:
                        json_data[key] = []
            return
        
        # Special handling for scorecard suggestions
        if self.step_name == "scorecard_suggestions":
            required_keys = ["ai_confidence", "priority_actions", "improvement_areas", "suggestions", "root_causes", "success_metrics", "explanation"]
            for key in required_keys:
                if key not in json_data:
                    if key == "explanation":
                        json_data[key] = self._extract_explanation_block(raw_output)
                    elif key == "ai_confidence":
                        json_data[key] = 0.0
                    elif key in ["priority_actions", "improvement_areas", "suggestions", "root_causes", "success_metrics"]:
                        json_data[key] = []
            return
        
        # Default handling for other tasks
        required_keys = ["sli", "slo", "alerts", "explanation", "llm_suggestions"]
        for key in required_keys:
            if key not in json_data:
                if key == "explanation":
                    json_data[key] = self._extract_explanation_block(raw_output)
                elif key in ["sli", "slo", "alerts", "llm_suggestions"]:
                    json_data[key] = [] if key != "llm_suggestions" else ["No suggestions provided."]

    def _clean_placeholders(self, data: Any) -> Any:
        if isinstance(data, str):
            return re.sub(r"\{\{\s*[^}]+\s*\}\}", "", data)
        elif isinstance(data, dict):
            return {k: self._clean_placeholders(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._clean_placeholders(v) for v in data]
        return data

    def _add_metadata(self, json_data: Dict[str, Any]) -> None:
        json_data["ai_model"] = self.model
        json_data["temperature"] = self.temperature

    def _calculate_confidence(self, json_data: Dict[str, Any]) -> None:
        confidence = 100
        if not json_data.get("explanation"):
            confidence -= 30
        if not json_data.get("llm_suggestions"):
            confidence -= 20
        if self.temperature > 0.8:
            confidence -= 20
        json_data["ai_confidence"] = max(confidence, 0)
        if json_data["ai_confidence"] < 60:
            logger.warning("⚠️ Low AI confidence in this response.")

    def clean_llm_output(self, data):
        # Special handling for drift suggestions
        if self.step_name == "drift_suggestions":
            allowed_fields = {"ai_confidence", "priority_actions", "improvement_areas", "suggestions", "root_causes", "success_metrics", "explanation"}
            data = {k: v for k, v in data.items() if k in allowed_fields}
            
            # Ensure all required fields are present and have correct types
            if "ai_confidence" not in data:
                data["ai_confidence"] = 0.0
            elif not isinstance(data["ai_confidence"], (int, float)):
                try:
                    data["ai_confidence"] = float(data["ai_confidence"])
                except (ValueError, TypeError):
                    data["ai_confidence"] = 0.0
            
            # Convert ai_confidence to decimal if it's a percentage (e.g., 80 -> 0.8)
            if isinstance(data["ai_confidence"], (int, float)):
                if data["ai_confidence"] > 1.0:
                    # Likely a percentage, convert to decimal
                    data["ai_confidence"] = data["ai_confidence"] / 100.0
                # Ensure it's within bounds
                data["ai_confidence"] = max(0.0, min(1.0, data["ai_confidence"]))
            
            for field in ["priority_actions", "improvement_areas", "suggestions", "root_causes", "success_metrics"]:
                if field not in data or not isinstance(data[field], list):
                    data[field] = []
            
            if "explanation" not in data or not data["explanation"]:
                data["explanation"] = "Generated suggestions based on drift analysis"
            
            return data
        
        # Special handling for scorecard suggestions
        if self.step_name == "scorecard_suggestions":
            allowed_fields = {"ai_confidence", "priority_actions", "improvement_areas", "suggestions", "root_causes", "success_metrics", "explanation"}
            data = {k: v for k, v in data.items() if k in allowed_fields}
            
            # Ensure all required fields are present and have correct types
            if "ai_confidence" not in data:
                data["ai_confidence"] = 0.0
            elif not isinstance(data["ai_confidence"], (int, float)):
                try:
                    data["ai_confidence"] = float(data["ai_confidence"])
                except (ValueError, TypeError):
                    data["ai_confidence"] = 0.0
            
            # Convert ai_confidence to decimal if it's a percentage (e.g., 80 -> 0.8)
            if isinstance(data["ai_confidence"], (int, float)):
                if data["ai_confidence"] > 1.0:
                    # Likely a percentage, convert to decimal
                    data["ai_confidence"] = data["ai_confidence"] / 100.0
                # Ensure it's within bounds
                data["ai_confidence"] = max(0.0, min(1.0, data["ai_confidence"]))
            
            for field in ["priority_actions", "improvement_areas", "suggestions", "root_causes", "success_metrics"]:
                if field not in data or not isinstance(data[field], list):
                    data[field] = []
            
            if "explanation" not in data or not data["explanation"]:
                data["explanation"] = "Generated suggestions based on scorecard analysis"
            
            return data
        
        # Only keep allowed top-level fields for other tasks
        allowed_fields = {"slo", "sli", "alerts", "explanation", "llm_suggestions"}
        data = {k: v for k, v in data.items() if k in allowed_fields}

        # Ensure 'slo' key exists and is a list, and not empty
        if "slo" not in data or not isinstance(data["slo"], list) or not data["slo"]:
            # Insert a context-aware default SLO if possible
            if "sli" in data and isinstance(data["sli"], list) and data["sli"]:
                first_sli = data["sli"][0]
                sli_type = first_sli.get("type", "custom").lower()
                sli_name = first_sli.get("name", "unknown")
                target = 99.0
                time_window = "30d"
                description = f"Auto-generated SLO for {sli_name}"
                if sli_type == "availability":
                    target = 99.9
                    time_window = "30d"
                    description = f"Ensure {sli_name} is available at least 99.9% of the time over a 30-day window."
                elif sli_type == "latency":
                    target = 0.95
                    time_window = "7d"
                    description = f"95% of requests for {sli_name} complete in under 200ms over a 7-day window."
                elif sli_type == "error":
                    target = 0.99
                    time_window = "30d"
                    description = f"Keep error rate for {sli_name} below 1% over a 30-day window."
                elif sli_type == "queue":
                    target = 0.9
                    time_window = "7d"
                    description = f"Queue utilization for {sli_name} remains below 90% over a 7-day window."
                elif sli_type == "saturation":
                    target = 0.85
                    time_window = "7d"
                    description = f"Saturation for {sli_name} remains below 85% over a 7-day window."
                elif sli_type == "utilization":
                    target = 0.8
                    time_window = "7d"
                    description = f"Utilization for {sli_name} remains below 80% over a 7-day window."
                elif sli_type in ["throughput", "custom"]:
                    target = round(float(first_sli.get("value", 100)) * 0.8, 2)
                    time_window = "7d"
                    description = f"Throughput for {sli_name} remains above {target} over a 7-day window."
                data["slo"] = [{
                    "name": f"Default SLO for {sli_name}",
                    "description": description,
                    "sli": sli_name,
                    "target": target,
                    "time_window": time_window
                }]
            else:
                data["slo"] = []

        # --- SLI cleaning ---
        allowed_sli_types = {"availability", "latency", "error", "throughput", "queue", "saturation", "utilization", "custom"}
        sli_allowed = {"name", "description", "type", "unit", "source", "metric", "value"}
        cleaned_sli = []
        if "sli" in data and isinstance(data["sli"], list):
            for sli in data["sli"]:
                if not isinstance(sli, dict):
                    continue
                # Coerce type
                sli_type = sli.get("type", "").strip().lower()
                if sli_type not in allowed_sli_types:
                    # Try to infer from name or metric
                    if "latency" in sli.get("name", "") or "latency" in sli.get("metric", ""):
                        sli_type = "latency"
                    elif "error" in sli.get("name", "") or "error" in sli.get("metric", ""):
                        sli_type = "error"
                    elif "avail" in sli.get("name", "") or "avail" in sli.get("metric", ""):
                        sli_type = "availability"
                    else:
                        sli_type = "custom"
                # Fill required fields
                cleaned = {
                    "name": sli.get("name", "unknown"),
                    "description": sli.get("description", ""),
                    "type": sli_type,
                    "unit": sli.get("unit", ""),
                    "source": sli.get("source", "prometheus"),
                    "metric": sli.get("metric", ""),
                    "value": sli.get("value", ""),
                    "threshold": sli.get("threshold", ""),
                    "duration": sli.get("duration", "")
                }
                # Remove unknown fields
                cleaned = {k: v for k, v in cleaned.items() if k in sli_allowed}
                cleaned_sli.append(cleaned)
            data["sli"] = cleaned_sli
        else:
            data["sli"] = []

        # --- SLO cleaning ---
        slo_allowed = {"name", "description", "sli", "target", "time_window"}
        allowed_time_windows = {"7d", "30d", "90d"}
        if "slo" in data and isinstance(data["slo"], list):
            cleaned_slos = []
            for slo in data["slo"]:
                if not isinstance(slo, dict):
                    continue
                
                # Ensure required fields are present
                cleaned_slo = {
                    "name": slo.get("name", "unnamed-slo"),
                    "description": slo.get("description", ""),
                    "sli": slo.get("sli", ""),
                    "target": slo.get("target", 99.0),
                    "time_window": slo.get("time_window", "30d")
                }
                
                # Fix slo.sli to be a string (use first element if list)
                if isinstance(cleaned_slo["sli"], list) and cleaned_slo["sli"]:
                    cleaned_slo["sli"] = str(cleaned_slo["sli"][0])
                
                # If sli is still empty, try to infer from available SLIs
                if not cleaned_slo["sli"] and "sli" in data and isinstance(data["sli"], list) and data["sli"]:
                    # Use the first available SLI
                    cleaned_slo["sli"] = data["sli"][0].get("name", "unknown")
                
                # Enforce allowed time_window
                if cleaned_slo["time_window"] not in allowed_time_windows:
                    cleaned_slo["time_window"] = "30d"
                
                # Coerce target to float
                try:
                    cleaned_slo["target"] = float(cleaned_slo["target"])
                except (ValueError, TypeError):
                    cleaned_slo["target"] = 99.0
                
                # Only keep allowed fields
                cleaned_slo = {k: v for k, v in cleaned_slo.items() if k in slo_allowed}
                cleaned_slos.append(cleaned_slo)
            
            data["slo"] = cleaned_slos
        else:
            data["slo"] = []

        # --- Alerts cleaning ---
        alert_allowed = {"name", "description", "severity", "expr", "for", "threshold", "duration"}
        allowed_severities = {"info", "warning", "critical"}
        if "alerts" in data and isinstance(data["alerts"], list):
            for alert in data["alerts"]:
                # Ensure every alert has a non-empty name
                if "name" not in alert or not alert["name"]:
                    alert["name"] = "unnamed-alert"
                keys = list(alert.keys())
                for k in keys:
                    if k not in alert_allowed:
                        del alert[k]
                if "severity" in alert and alert["severity"] not in allowed_severities:
                    alert["severity"] = "warning"
        # --- llm_suggestions cleaning ---
        if "llm_suggestions" in data and isinstance(data["llm_suggestions"], list):
            cleaned_suggestions = []
            for suggestion in data["llm_suggestions"]:
                if isinstance(suggestion, dict):
                    # Already in correct format, just ensure it has required fields
                    cleaned_suggestion = {
                        "metric": suggestion.get("metric", "unknown"),
                        "recommendation": suggestion.get("recommendation", "")
                    }
                    # Add any additional fields that might be present
                    for key, value in suggestion.items():
                        if key not in ["metric", "recommendation"]:
                            cleaned_suggestion[key] = value
                    cleaned_suggestions.append(cleaned_suggestion)
                elif isinstance(suggestion, str):
                    # Convert string to proper format
                    cleaned_suggestions.append({
                        "metric": "general",
                        "recommendation": suggestion
                    })
                else:
                    # Skip invalid suggestions
                    continue
            
            # Filter for suggestions with numbers (as per existing logic)
            def has_number(suggestion):
                if isinstance(suggestion, dict):
                    text = suggestion.get("recommendation", "")
                else:
                    text = str(suggestion)
                return bool(re.search(r"\d", text))
            
            filtered = [s for s in cleaned_suggestions if has_number(s)]
            if not filtered:
                filtered = [
                    {"metric": "unknown", "recommendation": "No specific numeric recommendation was generated."}
                ]
            data["llm_suggestions"] = filtered
        else:
            data["llm_suggestions"] = [
                {"metric": "unknown", "recommendation": "No suggestions provided."}
            ]
        # --- Explanation ---
        if "explanation" not in data or not isinstance(data["explanation"], str) or not data["explanation"].strip():
            data["explanation"] = "No explanation provided."
        # Ensure 'alerts' key exists and is a list, and not empty
        if "alerts" not in data or not isinstance(data["alerts"], list) or not data["alerts"]:
            # Insert a context-aware default alert if possible
            if "sli" in data and isinstance(data["sli"], list) and data["sli"]:
                first_sli = data["sli"][0]
                sli_type = first_sli.get("type", "custom").lower()
                sli_name = first_sli.get("name", "unknown")
                
                # Safely convert value to float, handling empty strings and invalid values
                raw_value = first_sli.get("value", 100)
                try:
                    if isinstance(raw_value, str) and raw_value.strip() == "":
                        value = 100.0  # Default value for empty strings
                    else:
                        value = float(raw_value)
                except (ValueError, TypeError):
                    value = 100.0  # Default value for invalid conversions
                
                threshold = 90
                duration = "5m"
                description = f"Auto-generated alert for {sli_name}"
                if sli_type == "availability":
                    threshold = 99.0
                    duration = "10m"
                    description = f"Alert if {sli_name} availability falls below {threshold}% for {duration}."
                elif sli_type == "latency":
                    threshold = 200
                    duration = "5m"
                    description = f"Alert if {sli_name} latency exceeds {threshold}ms for {duration}."
                elif sli_type == "error":
                    threshold = 1.0
                    duration = "10m"
                    description = f"Alert if {sli_name} error rate exceeds {threshold}% for {duration}."
                elif sli_type == "queue":
                    threshold = 90.0
                    duration = "10m"
                    description = f"Alert if {sli_name} queue utilization exceeds {threshold}% for {duration}."
                elif sli_type == "saturation":
                    threshold = 85.0
                    duration = "10m"
                    description = f"Alert if {sli_name} saturation exceeds {threshold}% for {duration}."
                elif sli_type == "utilization":
                    threshold = 80.0
                    duration = "10m"
                    description = f"Alert if {sli_name} utilization exceeds {threshold}% for {duration}."
                elif sli_type in ["throughput", "custom"]:
                    threshold = round(value * 0.8, 2)
                    duration = "10m"
                    description = f"Alert if {sli_name} throughput falls below {threshold} for {duration}."
                data["alerts"] = [{
                    "name": f"Default Alert for {sli_name}",
                    "description": description,
                    "threshold": threshold,
                    "duration": duration
                }]
            else:
                data["alerts"] = []
        return data


class SLIDataFetcher:
    def __init__(self, adapter=None):
        self.adapter = adapter or load_metrics_adapter(CONFIG.metrics)

    def fetch_sli_data(self, service: str, timeframe: str = "3m") -> List[Dict[str, Any]]:
        if not self.adapter:
            logger.warning("⚠️ No adapter provided — cannot fetch live data.")
            return []

        logger.info("🔌 Adapter provided — fetching live...")
        sli_types = ["availability", "latency", "error_rate"]
        sli_inputs = []

        for sli_type in sli_types:
            logger.info(f"🔍 Fetching type '{sli_type}' for component '{service}' with timeframe '{timeframe}'...")
            result = self.adapter.query_sli(component=service, sli_type=sli_type, timeframe=timeframe)
            if result:
                logger.info(f"✅ Received result: {result}")
                # Format SLI data according to template requirements
                sli_data = {
                    "component": service,
                    "sli_type": sli_type,
                    "value": result.value,
                    "unit": result.unit,
                    "query": result.query,
                    "source": result.source,
                    "metadata": result.metadata
                }
                sli_inputs.append(sli_data)

        logger.info(f"📊 Fetched {len(sli_inputs)} live records.")
        return sli_inputs


async def generate_prompt_response(
    input_json: dict,
    template='default',
    explain=True,
    model='llama2',
    adapter=None,
    temperature=0.7,
    prompt=None,
    mode="default",
    provider="ollama"
) -> dict:
    try:
        Path("debug").mkdir(parents=True, exist_ok=True)
        
        # Check for scorecard suggestions task
        task = input_json.get("task")
        if task == "scorecard_suggestions":
            return await generate_scorecard_suggestions_response(input_json, model, temperature, provider)
        elif task == "drift_suggestions":
            return await generate_drift_suggestions_response(input_json, model, temperature, provider)
        
        # Initialize components
        template_manager = TemplateManager()
        response_processor = ResponseProcessor(model, temperature, input_context=input_json)
        sli_fetcher = SLIDataFetcher(adapter)

        # Get service name and prepare context
        service_name = input_json.get("service") or input_json.get("service_name", "service")
        context = {"service_name": service_name}

        # Fetch SLI data if needed
        timeframe = input_json.get("timeframe", "3m")
        if not input_json.get("sli_inputs"):
            input_json["sli_inputs"] = sli_fetcher.fetch_sli_data(service_name, timeframe)

        # Render SLI fields
        input_json["sli_inputs"] = template_manager.render_sli_fields(
            input_json.get("sli_inputs", []),
            context
        )

        # Generate prompt
        if not prompt:
            prompt = template_manager.render_template(template, {
                "service_name": service_name,
                "sli_inputs": input_json.get("sli_inputs", []),
                "sli_quantity": input_json.get("sli_quantity", 5),
                "slo_quantity": input_json.get("slo_quantity", 3),
                "alert_quantity": input_json.get("alert_quantity", 3),
                "suggestion_quantity": input_json.get("suggestion_quantity", 5)
            })

        # Save debug information
        try:
            Path("debug/last_prompt.txt").write_text(prompt)
        except Exception as e:
            logger.error(f"❌ Failed to write last_prompt.txt: {e}")

        # Handle minimal mode
        if mode == "minimal":
            explain = False
            logger.info("⚙️  Minimal mode: Advanced LLM capabilities will be disabled.")

        # Call LLM and process response
        logger.info(f"📤 Sending prompt to LLM (provider={provider}, model={model}) with temperature={temperature}")
        raw_output = call_llm(prompt, explain=explain, model=model, temperature=temperature, provider=provider)
        print("Full LLM output:", raw_output)
        Path("core/output/").mkdir(exist_ok=True)
        Path(f"core/output/{template}_output.txt").write_text(raw_output)

        output = response_processor.process_response(raw_output, explain)
        # Ensure 'value' and 'explanation' are present in each SLI in the 'sli' section
        if "sli_inputs" in input_json and input_json["sli_inputs"] and "sli" in output:
            input_sli_map = {sli["name"]: sli for sli in input_json["sli_inputs"] if "name" in sli}
            for sli in output["sli"]:
                name = sli.get("name")
                if name and name in input_sli_map:
                    input_sli = input_sli_map[name]
                    if "value" in input_sli:
                        sli["value"] = input_sli["value"]
                    if "explanation" in input_sli:
                        sli["explanation"] = input_sli["explanation"]
        return output

    except Exception as e:
        logger.error(f"❌ Error during prompt generation: {e}")
        raise

async def generate_scorecard_suggestions_response(input_json: dict, model: str, temperature: float, provider: str) -> dict:
    """Generate LLM suggestions based on scorecard data"""
    try:
        from backend.core.services.prompt.templates.scorecard_suggestions import SCORECARD_SUGGESTIONS_TEMPLATE
        
        # Extract data from input
        scorecard_data = input_json.get("scorecard_data", {})
        service_name = input_json.get("service_name") or "All Services"
        analysis_period_days = input_json.get("analysis_period_days", 30)
        current_timestamp = input_json.get("current_timestamp", "")
        
        # Format scorecard data for the prompt
        formatted_scorecard = json.dumps(scorecard_data, indent=2)
        
        # Generate prompt using the template
        prompt = SCORECARD_SUGGESTIONS_TEMPLATE.format(
            scorecard_data=formatted_scorecard,
            service_name=service_name,
            analysis_period_days=analysis_period_days,
            current_timestamp=current_timestamp
        )
        
        # Call LLM
        logger.info(f"📤 Generating scorecard suggestions (provider={provider}, model={model})")
        raw_output = call_llm(prompt, explain=False, model=model, temperature=temperature, provider=provider)
        
        # Process response
        response_processor = ResponseProcessor(model, temperature, "scorecard_suggestions", input_context=input_json)
        output = response_processor.process_response(raw_output, explain=False)
        
        return output
        
    except Exception as e:
        logger.error(f"❌ Error generating scorecard suggestions: {e}")
        # Return fallback suggestions
        return generate_fallback_suggestions(input_json.get("scorecard_data", {}))

async def generate_drift_suggestions_response(input_json: dict, model: str, temperature: float, provider: str) -> dict:
    """Generate LLM suggestions based on drift analysis data"""
    try:
        from backend.core.services.prompt.templates.drift_suggestions import DRIFT_SUGGESTIONS_TEMPLATE
        
        # Extract data from input
        drift_data = input_json.get("drift_data", {})
        service_name = input_json.get("service_name") or "All Services"
        analysis_period_days = input_json.get("analysis_period_days", 30)
        current_timestamp = input_json.get("current_timestamp", "")
        
        # Format drift data for the prompt
        formatted_drift = json.dumps(drift_data, indent=2)
        
        # Generate prompt using the template
        prompt = DRIFT_SUGGESTIONS_TEMPLATE.format(
            drift_data=formatted_drift,
            service_name=service_name,
            analysis_period_days=analysis_period_days,
            current_timestamp=current_timestamp
        )
        
        # Call LLM
        logger.info(f"📤 Generating drift suggestions (provider={provider}, model={model})")
        raw_output = call_llm(prompt, explain=False, model=model, temperature=temperature, provider=provider)
        
        # Process response
        response_processor = ResponseProcessor(model, temperature, "drift_suggestions", input_context=input_json)
        output = response_processor.process_response(raw_output, explain=False)
        
        return output
        
    except Exception as e:
        logger.error(f"❌ Error generating drift suggestions: {e}")
        # Return fallback suggestions
        return generate_drift_fallback_suggestions(input_json.get("drift_data", {}))

def generate_drift_fallback_suggestions(drift_data: dict) -> dict:
    """Generate basic suggestions when LLM is unavailable for drift analysis"""
    return {
        "ai_confidence": 0.0,
        "priority_actions": [
            "Review drift metrics for concerning trends",
            "Focus on the most declining metric first",
            "Implement monitoring for drift tracking"
        ],
        "improvement_areas": ["Overall system stability"],
        "suggestions": [
            "Analyze the drift breakdown to identify specific issues",
            "Set up alerts for when drift exceeds thresholds",
            "Create action plans for each drift area"
        ],
        "root_causes": ["Insufficient data for detailed analysis"],
        "success_metrics": [
            "Reduction in drift magnitude",
            "Stabilization of key metrics",
            "Improved consistency over time"
        ],
        "explanation": "Generated basic suggestions due to LLM unavailability"
    }

def generate_fallback_suggestions(scorecard_data: dict) -> dict:
    """Generate basic suggestions when LLM is unavailable"""
    return {
        "ai_confidence": 0.0,
        "priority_actions": [
            "Review scorecard metrics for areas below 80%",
            "Focus on the lowest-scoring metric first",
            "Implement monitoring for improvement tracking"
        ],
        "improvement_areas": ["Overall system performance"],
        "suggestions": [
            "Analyze the scorecard breakdown to identify specific issues",
            "Set up alerts for when metrics fall below thresholds",
            "Create action plans for each improvement area"
        ],
        "root_causes": ["Insufficient data for detailed analysis"],
        "success_metrics": [
            "Improvement in overall scorecard score",
            "Reduction in failed validations",
            "Increased consistency in outputs"
        ],
        "explanation": "Generated basic suggestions due to LLM unavailability"
    }

def generate_definitions(
    input_path: str,
    output_path: str,
    template: str,
    explain: bool,
    model: str,
    show_suggestions: bool = True,
    adapter=None,
    temperature: float = 0.7,
    rag: bool = False,
    mode: str = "default"
):
    try:
        print("📍 generate_definitions() was called")
        logger.info(f"📥 Loading input file: {input_path}")
        
        # Load input JSON
        input_json = json.loads(Path(input_path).read_text())
        json_temp = input_json.get("temperature")
        final_temperature = float(json_temp) if json_temp is not None else temperature
        logger.info(f"🌡️  Using temperature={final_temperature}")

        # Initialize components
        template_manager = TemplateManager()
        sli_fetcher = SLIDataFetcher(adapter)

        # Fetch SLI data if needed
        timeframe = input_json.get("timeframe", "3m")
        if not input_json.get("sli_inputs"):
            component = input_json.get("service") or input_json.get("service_name", "api")
            input_json["sli_inputs"] = sli_fetcher.fetch_sli_data(component, timeframe)

        # Generate prompt
        if Path(template).suffix == ".j2":
            prompt = None
        else:
            prompt = template_manager.render_template(template, {
                "service_name": input_json.get("service") or input_json.get("service_name", "api"),
                "sli_inputs": input_json.get("sli_inputs", [])
            })

        # Generate response
        json_data = generate_prompt_response(
            input_json=input_json,
            prompt=prompt,
            template=template,
            explain=(explain if mode != "minimal" else False),
            model=model,
            adapter=adapter,
            temperature=final_temperature,
            mode=mode
        )

        # Save output
        Path(output_path).write_text(json.dumps(json_data, indent=2))
        logger.info(f"✅ Output written to {output_path}")
        print(json.dumps(json_data, indent=2))

    except Exception as e:
        logger.error(f"❌ Error during generation: {e}")
        raise

def generate_prompt_response_5step(
    input_json: dict,
    model='llama2',
    adapter=None,
    temperature=0.7,
    mode="default",
    provider="ollama"
) -> dict:
    """
    Generate observability configuration using the 5-step LLM process.
    
    Steps:
    1. SLI Discovery & Validation
    2. SLO Generation  
    3. Alert Rule Creation
    4. Analysis & Recommendations
    5. Validation & Integration
    """
    try:
        Path("debug").mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        template_manager = TemplateManager()
        sli_fetcher = SLIDataFetcher(adapter)

        # Get service name and prepare context
        service_name = input_json.get("service") or input_json.get("service_name", "service")
        context = {"service_name": service_name}

        # Fetch SLI data if needed
        timeframe = input_json.get("timeframe", "3m")
        if not input_json.get("sli_inputs"):
            input_json["sli_inputs"] = sli_fetcher.fetch_sli_data(service_name, timeframe)

        # Render SLI fields
        input_json["sli_inputs"] = template_manager.render_sli_fields(
            input_json.get("sli_inputs", []),
            context
        )

        logger.info("🚀 Starting 5-step LLM process...")
        
        # Step 1: SLI Discovery & Validation
        logger.info("📊 Step 1: SLI Discovery & Validation")
        step1_context = {
            "service_name": service_name,
            "description": input_json.get("description", "No description provided."),
            "metrics": input_json.get("metrics", []),
            "sli_quantity": input_json.get("sli_quantity", 5),
            "timeframe": timeframe
        }
        step1_prompt = template_manager.render_template("step1_sli_discovery", step1_context)
        step1_processor = ResponseProcessor(model, temperature, "step1_sli_discovery", input_context=input_json)
        step1_output = call_llm(step1_prompt, explain=False, model=model, temperature=temperature, provider=provider)
        step1_data = step1_processor.process_response(step1_output, explain=False)
        
        # Save step 1 debug info
        Path("debug/step1_sli_discovery.txt").write_text(step1_output)
        logger.info(f"✅ Step 1 completed: {len(step1_data.get('sli', []))} SLIs discovered")

        # Step 2: SLO Generation
        logger.info("🎯 Step 2: SLO Generation")
        step2_context = {
            "service_name": service_name,
            "description": input_json.get("description", "No description provided."),
            "sli_inputs": step1_data.get("sli", []),
            "slo_quantity": input_json.get("slo_quantity", 3),
            "timeframe": timeframe
        }
        step2_prompt = template_manager.render_template("step2_slo_generation", step2_context)
        step2_processor = ResponseProcessor(model, temperature, "step2_slo_generation", input_context=input_json)
        step2_output = call_llm(step2_prompt, explain=False, model=model, temperature=temperature, provider=provider)
        step2_data = step2_processor.process_response(step2_output, explain=False)
        
        # Save step 2 debug info
        Path("debug/step2_slo_generation.txt").write_text(step2_output)
        logger.info(f"✅ Step 2 completed: {len(step2_data.get('slo', []))} SLOs generated")

        # Step 3: Alert Rule Creation
        logger.info("🚨 Step 3: Alert Rule Creation")
        step3_context = {
            "service_name": service_name,
            "description": input_json.get("description", "No description provided."),
            "slo_inputs": step2_data.get("slo", []),
            "sli_inputs": step1_data.get("sli", []),
            "alert_quantity": input_json.get("alert_quantity", 3),
            "timeframe": timeframe
        }
        step3_prompt = template_manager.render_template("step3_alert_creation", step3_context)
        step3_processor = ResponseProcessor(model, temperature, "step3_alert_creation", input_context=input_json)
        step3_output = call_llm(step3_prompt, explain=False, model=model, temperature=temperature, provider=provider)
        step3_data = step3_processor.process_response(step3_output, explain=False)
        
        # Save step 3 debug info
        Path("debug/step3_alert_creation.txt").write_text(step3_output)
        logger.info(f"✅ Step 3 completed: {len(step3_data.get('alerts', []))} alerts created")

        # Step 4: Analysis & Recommendations
        logger.info("📈 Step 4: Analysis & Recommendations")
        step4_context = {
            "service_name": service_name,
            "description": input_json.get("description", "No description provided."),
            "sli_inputs": step1_data.get("sli", []),
            "slo_inputs": step2_data.get("slo", []),
            "alert_inputs": step3_data.get("alerts", []),
            "suggestion_quantity": input_json.get("suggestion_quantity", 5),
            "timeframe": timeframe
        }
        step4_prompt = template_manager.render_template("step4_analysis_recommendations", step4_context)
        step4_processor = ResponseProcessor(model, temperature, "step4_analysis_recommendations", input_context=input_json)
        step4_output = call_llm(step4_prompt, explain=False, model=model, temperature=temperature, provider=provider)
        step4_data = step4_processor.process_response(step4_output, explain=False)
        
        # Save step 4 debug info
        Path("debug/step4_analysis_recommendations.txt").write_text(step4_output)
        logger.info("✅ Step 4 completed: Analysis and recommendations generated")

        # Step 5: Validation & Integration
        logger.info("🔍 Step 5: Validation & Integration")
        
        # Integrate all data from previous steps
        integrated_data = {
            "sli": step1_data.get("sli", []),
            "slo": step2_data.get("slo", []),
            "alerts": step3_data.get("alerts", []),
            "explanation": step4_data.get("explanation", ""),
            "llm_suggestions": step4_data.get("llm_suggestions", []),
            "risk_assessment": step4_data.get("risk_assessment", {}),
            "coverage_gaps": step4_data.get("coverage_gaps", {}),
            "optimization_opportunities": step4_data.get("optimization_opportunities", [])
        }
        
        step5_context = {
            "service_name": service_name,
            "description": input_json.get("description", "No description provided."),
            "sli_inputs": step1_data.get("sli", []),
            "slo_inputs": step2_data.get("slo", []),
            "alert_inputs": step3_data.get("alerts", []),
            "analysis_explanation": step4_data.get("explanation", ""),
            "risk_level": step4_data.get("risk_assessment", {}).get("risk_level", "medium"),
            "coverage_score": step4_data.get("coverage_score", 75),
            "integrated_data": integrated_data,  # Pass the integrated data for validation
            "timeframe": timeframe
        }
        step5_prompt = template_manager.render_template("step5_validation_integration", step5_context)
        step5_processor = ResponseProcessor(model, temperature, "step5_validation_integration", input_context=input_json)
        step5_output = call_llm(step5_prompt, explain=False, model=model, temperature=temperature, provider=provider)
        step5_data = step5_processor.process_response(step5_output, explain=False)
        
        # If step5 doesn't return complete data, merge with integrated data
        # Always merge to ensure we have all data from previous steps
        if integrated_data.get("sli"):
            step5_data["sli"] = integrated_data["sli"]
        if integrated_data.get("slo"):
            step5_data["slo"] = integrated_data["slo"]
        if integrated_data.get("alerts"):
            step5_data["alerts"] = integrated_data["alerts"]
        if integrated_data.get("explanation"):
            step5_data["explanation"] = integrated_data["explanation"]
        if integrated_data.get("llm_suggestions"):
            step5_data["llm_suggestions"] = integrated_data["llm_suggestions"]
        
        # Add additional data from step4 if not present
        if integrated_data.get("risk_assessment"):
            step5_data["risk_assessment"] = integrated_data["risk_assessment"]
        if integrated_data.get("coverage_gaps"):
            step5_data["coverage_gaps"] = integrated_data["coverage_gaps"]
        if integrated_data.get("optimization_opportunities"):
            step5_data["optimization_opportunities"] = integrated_data["optimization_opportunities"]
        
        # Save step 5 debug info
        Path("debug/step5_validation_integration.txt").write_text(step5_output)
        logger.info("✅ Step 5 completed: Final validation and integration")

        # Ensure 'value' and 'explanation' are present in each SLI
        if "sli_inputs" in input_json and input_json["sli_inputs"] and "sli" in step5_data:
            input_sli_map = {sli["name"]: sli for sli in input_json["sli_inputs"] if "name" in sli}
            for sli in step5_data["sli"]:
                name = sli.get("name")
                if name and name in input_sli_map:
                    input_sli = input_sli_map[name]
                    if "value" in input_sli:
                        sli["value"] = input_sli["value"]
                    if "explanation" in input_sli:
                        sli["explanation"] = input_sli["explanation"]

        # Add metadata about the 5-step process
        step5_data["metadata"] = {
            "generation_method": "5step_llm_process",
            "steps_completed": ["sli_discovery", "slo_generation", "alert_creation", "analysis", "validation"],
            "model": model,
            "temperature": temperature,
            "service_name": service_name
        }

        # Prepare step-by-step data for frontend
        step_data = {
            "step1_sli_discovery": {
                "raw_output": step1_output[:2000] + "..." if len(step1_output) > 2000 else step1_output,
                "processed_data": step1_data,
                "description": "SLI Discovery & Validation"
            },
            "step2_slo_generation": {
                "raw_output": step2_output[:2000] + "..." if len(step2_output) > 2000 else step2_output,
                "processed_data": step2_data,
                "description": "SLO Generation"
            },
            "step3_alert_creation": {
                "raw_output": step3_output[:2000] + "..." if len(step3_output) > 2000 else step3_output,
                "processed_data": step3_data,
                "description": "Alert Rule Creation"
            },
            "step4_analysis_recommendations": {
                "raw_output": step4_output[:2000] + "..." if len(step4_output) > 2000 else step4_output,
                "processed_data": step4_data,
                "description": "Analysis & Recommendations"
            },
            "step5_validation_integration": {
                "raw_output": step5_output[:2000] + "..." if len(step5_output) > 2000 else step5_output,
                "processed_data": step5_data,
                "description": "Validation & Integration"
            }
        }

        # Return both final data and step data
        result = {
            "final_data": step5_data,
            "step_data": step_data,
            "metadata": {
                "generation_method": "5step_llm_process",
                "steps_completed": ["sli_discovery", "slo_generation", "alert_creation", "analysis", "validation"],
                "model": model,
                "temperature": temperature,
                "service_name": service_name,
                "total_steps": 5
            }
        }

        logger.info("🎉 5-step LLM process completed successfully!")
        return result

    except Exception as e:
        logger.error(f"❌ Error during 5-step LLM process: {e}")
        raise