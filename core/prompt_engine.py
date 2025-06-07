# core/prompt_engine.py

import re
import json
import textwrap
from pathlib import Path
from llm.interface import call_llm
from core.logger import logger
from core.basic_validator import basic_output_shape_check

# 🔌 New import for metrics
from core.config import CONFIG
from metrics.loader import load_metrics_adapter


def generate_prompt_response(input_json: dict, template='default', explain=True, model='ollama') -> dict:
    try:
        Path("debug").mkdir(parents=True, exist_ok=True)
        template_path = Path(template) if Path(template).is_file() else Path("core/prompt_templates") / f"{template}.j2"
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        logger.info(f"📨 Using template: {template}")
        prompt_template = template_path.read_text()
        prompt = prompt_template.replace("{input}", json.dumps(input_json, indent=2))
        Path("debug/last_prompt.txt").write_text(prompt)

        logger.info(f"📤 Sending prompt to LLM (provider={model})...")
        raw_output = call_llm(prompt, explain=explain, model=model)
        output_path = Path("core/output/") / f"{template}_output.txt"
        output_path.write_text(raw_output)

        # Try first parse
        try:
            json_data = extract_json_block(raw_output)
        except ValueError as e:
            logger.warning(f"⚠️ First parse failed: {e}")
            logger.info("🔁 Retrying LLM with stricter prompt...")
            retry_prompt = prompt + "\n\n🔁 Retry: Return ONLY a valid JSON object with no explanation."
            raw_output = call_llm(retry_prompt, explain=False, model=model)
            output_path.write_text(raw_output)  # Overwrite with retry
            json_data = extract_json_block(raw_output)

        if explain and not json_data.get("explanation"):
            logger.warning("⚠️ Missing 'explanation' in JSON. Attempting extraction from raw output.")
            json_data["explanation"] = extract_explanation_block(raw_output).strip()

        required_keys = ["sli", "slo", "alerts", "explanation", "llm_suggestions"]
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
        input_data = Path(input_path).read_text()
        input_json = json.loads(input_data)

        # 🔌 Load metrics adapter
        adapter = load_metrics_adapter(CONFIG)
        sli_results = []
        for obj in input_json.get("objectives", []):
            component = obj["component"]
            sli_type = obj.get("sli_type", "availability")
            sli = adapter.query_sli(component=component, sli_type=sli_type)
            if sli:
                sli_results.append(sli)

        # 🔁 Fallback to static adapter if nothing found
        if not sli_results:
            logger.warning("⚠️ No live SLI data found. Falling back to static source.")
            fallback_adapter = load_metrics_adapter({"metrics_provider": "static", "static_path": CONFIG.get("static_path")})
            sli_results = fallback_adapter.load_all()

        input_json["live_sli_data"] = sli_results
        logger.info(f"📊 Injected {len(sli_results)} SLI records into prompt input.")

        # 🧠 Generate LLM response
        json_data = generate_prompt_response(
            input_json,
            template=template,
            explain=explain,
            model=model
        )

        # 🖨️ Output
        logger.info("\n📄 JSON Output:\n" + "-" * 50 + f"\n{json.dumps(json_data, indent=2)}\n")
        print("\n📄 JSON Output:\n" + "-" * 50)
        print(json.dumps(json_data, indent=2))

        if explain:
            print("\n🧠 Explanation:\n" + "-" * 50)
            print(json_data.get("explanation", ""))

        if show_suggestions:
            suggestions = json_data.get("llm_suggestions", [])
            if isinstance(suggestions, list) and suggestions:
                print("\n💡 LLM Suggestions:\n" + "-" * 50)
                for suggestion in suggestions:
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

            # 🔧 Attempt to fix common formatting issues
            fixed = re.sub(r'"\s+"', '", "', json_str)  # missing comma
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