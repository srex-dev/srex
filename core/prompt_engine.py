import json
import textwrap
from pathlib import Path
from llm.interface import call_llm
from core.logger import logger
from core.schema import validate_slo_json, validate_sli_json, validate_alert_json


def get_validator(template_name: str):
    if template_name == "observability":
        return validate_sli_json
    elif template_name == "slo":
        return validate_slo_json
    elif template_name == "alert":
        return validate_alert_json

def generate_definitions(input_path: str, output_path: str, template: str, explain: bool, model: str):
    try:
        logger.info(f"📥 Loading input file: {input_path}")
        input_data = Path(input_path).read_text()
        input_json = json.loads(input_data)

        template_path = f"prompt_templates/{template}.txt"
        logger.info(f"🧩 Using template: {template_path}")
        prompt_template = Path(template_path).read_text()
        prompt = prompt_template.replace("{input}", json.dumps(input_json, indent=2))

        logger.info(f"📤 Sending prompt to LLM (provider={model})...")
        raw_output = call_llm(prompt, explain=explain, model=model)
        logger.info("✅ LLM response received successfully.")
        logger.info("📄 Raw LLM output:\n" + "-" * 50 + f"\n{raw_output}\n")

        json_data = extract_json_block(raw_output)

        if explain and "explanation" not in json_data:
            explanation = extract_explanation_block(raw_output)
            json_data["explanation"] = explanation.strip()
        elif explain:
            explanation = json_data.get("explanation", "").strip()
        else:
            explanation = ""

        logger.info("\n📄 JSON Output:\n" + "-" * 50 + f"\n{json.dumps(json_data, indent=2)}\n")
        logger.info("\n🧠 Explanation:\n" + "-" * 50 + f"\n{explanation}\n")

        print("\n📄 JSON Output:\n" + "-" * 50)
        print(json.dumps(json_data, indent=2))
        print("\n🧠 Explanation:\n" + "-" * 50)
        print(explanation)

        logger.info("🔍 Validating JSON...")

        validator = get_validator(template)
        validate_target = json_data.get("slo") if template != "observability" else json_data
        is_valid, errors = validator(validate_target)

        if not is_valid:
            logger.error(f"❌ JSON validation failed: {errors}")
            raise ValueError(f"Output JSON is invalid: {errors}")

        with open(output_path, "w") as f:
            json.dump(json_data, f, indent=2)

        logger.info(f"✅ Output JSON written to {output_path}")

    except Exception as e:
        logger.error(f"❌ Error during generation: {e}")
        raise


def extract_json_block(text: str) -> dict:
    try:
        start = text.index("{")
        brace_count = 0
        for i, c in enumerate(text[start:], start=start):
            if c == "{":
                brace_count += 1
            elif c == "}":
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        else:
            raise ValueError("JSON block not closed properly")

        json_block = text[start:end]
        return json.loads(json_block)

    except Exception as e:
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