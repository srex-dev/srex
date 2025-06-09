
# core/prompt_engine.py

import re
import json
import re
import json
import textwrap
from pathlib import Path
from jinja2 import Template
from llm.interface import call_llm
from core.logger import logger
from core.basic_validator import basic_output_shape_check
from core.config import CONFIG
from metrics.loader import load_metrics_adapter

def generate_prompt_response(input_json: dict, template='default', explain=True, model='ollama', adapter=None) -> dict:
    try:
        Path("debug").mkdir(parents=True, exist_ok=True)
        template_path = Path(template) if Path(template).is_file() else Path("core/prompt_templates") / f"{template}.j2"
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        # 🔌 Fetch live SLI data if adapter is provided
        if adapter and not input_json.get("sli_inputs"):
            logger.info("🔌 Adapter provided — fetching live SLIs...")
            service = input_json.get("service") or input_json.get("service_name")
            sli_types = ["availability", "latency", "error_rate"]
            sli_inputs = []
            for sli_type in sli_types:
                logger.info(f"🔍 Fetching SLI type '{sli_type}' for component '{service}'...")
                result = adapter.query_sli(component=service, sli_type=sli_type)
                if result:
                    logger.info(f"✅ Received SLI result: {result}")
                    sli_inputs.append({
                        "component": service,
                        "sli_type": sli_type,
                        "value": result["value"],
                        "unit": result["unit"],
                        "query": result["query"],
                        "source": result["source"]
                    })
            input_json["sli_inputs"] = sli_inputs
            logger.info(f"📊 Injected {len(sli_inputs)} live SLI records into prompt input.")


        service_name = input_json.get("service") or input_json.get("service_name", "service")
        context = {"service_name": service_name}
        for sli in input_json.get("sli_inputs", []):
            for field in ["query", "name", "description", "metric", "source"]:
                if field in sli and isinstance(sli[field], str) and "{{" in sli[field]:
                    try:
                        sli[field] = Template(sli[field]).render(**context)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to render {field} for {sli.get('name', 'unknown')}: {e}")

        logger.info(f"📨 Using template: {template}")
        prompt_template = template_path.read_text()
        prompt = prompt_template.replace("{input}", json.dumps(input_json, indent=2))
        Path("debug/last_prompt.txt").write_text(prompt)

        logger.info(f"📤 Sending prompt to LLM (provider={model})...")
        raw_output = call_llm(prompt, explain=explain, model=model)
        output_path = Path("core/output/") / f"{template}_output.txt"
        output_path.write_text(raw_output)

        try:
            json_data = extract_json_block(raw_output)
        except ValueError as e:
            logger.warning(f"⚠️ First parse failed: {e}")
            retry_prompt = prompt + "\n\n🔁 Retry: Return ONLY a valid JSON object with no explanation."
            raw_output = call_llm(retry_prompt, explain=False, model=model)
            output_path.write_text(raw_output)
            json_data = extract_json_block(raw_output)

        if explain and not json_data.get("explanation"):
            logger.warning("⚠️ Missing 'explanation' in JSON. Attempting extraction from raw output.")
            json_data["explanation"] = extract_explanation_block(raw_output).strip()

        required_keys = ["sli", "slo", "alerts", "explanation", "llm_suggestions"]
        for key in required_keys:
            if key not in json_data:
                logger.warning(f"⚠️ Missing key in LLM output: {key}")
                if key == "explanation":
                    json_data[key] = extract_explanation_block(raw_output)
                elif key in ["sli", "slo", "alerts", "llm_suggestions"]:
                    json_data[key] = [] if key != "llm_suggestions" else ["No suggestions provided."]

        # 🚫 Final cleanup: strip any leftover {{ ... }} templates from LLM response
        def clean_placeholders(value):
            if isinstance(value, str):
                return re.sub(r"\{\{.*?\}\}", "[UNRESOLVED]", value)
            return value

        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(clean_placeholders(v)) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(v) for v in d]
            else:
                return clean_placeholders(d)

        json_data = clean_dict(json_data)

        errors = basic_output_shape_check(json_data, required_keys)
        if errors:
            logger.warning("⚠️ Output structure issues:\n" + json.dumps(errors, indent=2))
        
        return json_data

    except Exception as e:
        logger.error(f"❌ Error during prompt generation: {e}")
        raise

def generate_definitions(input_path: str, output_path: str, template: str, explain: bool, model: str, show_suggestions: bool = True):
    try:
        logger.info(f"📥 Loading input file: {input_path}")
        input_json = json.loads(Path(input_path).read_text())

        adapter = load_metrics_adapter(CONFIG)

        if not input_json.get("sli_inputs"):
            logger.info("🔍 No SLI input found, attempting to fetch via adapter...")
            component = input_json.get("service") or input_json.get("service_name", "api")
            sli_types = ["availability", "latency", "error_rate"]
            sli_inputs = []
            for sli_type in sli_types:
                sli = adapter.query_sli(component=component, sli_type=sli_type)
                if sli:
                    sli_inputs.append({
                        "component": component,
                        "sli_type": sli_type,
                        "value": sli["value"],
                        "unit": sli["unit"],
                        "query": sli["query"],
                        "source": sli["source"]
                    })
            input_json["sli_inputs"] = sli_inputs

            service_name = input_json.get("service") or input_json.get("service_name", "service")
            for sli in input_json["sli_inputs"]:
                if "{{ service_name }}" in sli["query"]:
                    sli["query"] = sli["query"].replace("{{ service_name }}", service_name)

            logger.info(f"📊 Injected {len(sli_inputs)} live SLI records into prompt input.")

            if not sli_inputs:
                logger.warning("⚠️ No live SLI data found. Falling back to static source...")
                fallback_adapter = load_metrics_adapter({"metrics_provider": "static", "static_path": CONFIG.get("static_path")})
                input_json["sli_inputs"] = fallback_adapter.load_all()
                logger.info(f"📦 Fallback loaded {len(input_json['sli_inputs'])} static SLIs.")

        json_data = generate_prompt_response(
            input_json,
            template=template,
            explain=explain,
            model=model,
            adapter=adapter
        )

        logger.info("📄 JSON Output:\n" + "-" * 50 + f"\n{json.dumps(json_data, indent=2)}\n")
        print("\n📄 JSON Output:\n" + "-" * 50)
        print(json.dumps(json_data, indent=2))

        if explain:
            print("\n🧠 Explanation:\n" + "-" * 50)
            print(json_data.get("explanation", ""))

        if show_suggestions and json_data.get("llm_suggestions"):
            print("\n💡 LLM Suggestions:\n" + "-" * 50)
            for suggestion in json_data["llm_suggestions"]:
                print(f"- {suggestion}")

        Path(output_path).write_text(json.dumps(json_data, indent=2))
        logger.info(f"✅ Output JSON written to {output_path}")

    except Exception as e:
        logger.error(f"❌ Error during generation: {e}")
        raise


def extract_json_block(text: str) -> dict:
    try:
        logger.debug("📦 Raw LLM output before cleanup:\n" + text)

        cleaned = re.sub(r"```(?:json)?", "", text)
        cleaned = re.sub(r"[^\x20-\x7E\n\r\t]", "", cleaned).strip()

        logger.debug("🧹 Cleaned LLM output:\n" + cleaned)

        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No complete JSON object found.")

        json_str = cleaned[start:end + 1]
        logger.debug("🔍 Extracted JSON candidate:\n" + json_str)
        Path("debug/llm_cleaned_output.json").write_text(json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Standard parse failed: {e}")

            fixed = re.sub(r'"\s+"', '", "', json_str)
            fixed = re.sub(r'"\s+([a-zA-Z0-9_]+)"\s*:', r'", "\1":', fixed)

            sanitized = (
                fixed.replace('\\', '\\\\')
                     .replace('\\"', '"')
                     .replace('“', '"')
                     .replace('”', '"')
                     .replace('‘', "'")
                     .replace('’', "'")
                     .replace('"\n', '"')
            )

            logger.debug("🛠 Retrying parse with sanitized content...")
            return json.loads(sanitized)

    except Exception as e:
        debug_path = Path("debug/llm_broken_output.json")
        debug_path.write_text(text)
        raise ValueError(f"❌ Error parsing JSON block: {e}")


def extract_explanation_block(text: str) -> str:
    lines = text.replace("```", "").splitlines()
    start = False
    explanation_lines = []

    for line in lines:
        if start:
            explanation_lines.append(line)
        elif line.strip().lower().startswith("explanation:"):
            start = True
            explanation_lines.append(line)

    return textwrap.dedent("\n".join(explanation_lines)).strip()