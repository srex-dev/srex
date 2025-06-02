import json
import re
import textwrap
from pathlib import Path
from core.schema import validate_slo_json  # Updated validation function for JSON
from llm.interface import call_llm
from core.logger import logger


def generate_slo_definitions(input_path: str, output_path: str, template: str, explain: bool, provider: str = "ollama"):
    try:
        logger.info(f"Loading input file: {input_path}")
        input_data = Path(input_path).read_text()
        input_json = json.loads(input_data)  # Ensure it's valid JSON

        template_path = f"prompt_templates/{template}.txt"
        logger.info(f"Using template: {template_path}")
        prompt_template = Path(template_path).read_text()
        prompt = prompt_template.replace("{input}", json.dumps(input_json, indent=2))

        logger.info(f"Sending prompt to LLM ({provider})...")
        raw_output = call_llm(prompt, explain=explain)
        logger.info("✅ LLM response received successfully.")
        logger.info("📄 Raw LLM output:\n" + "-" * 50 + f"\n{raw_output}\n")

        json_data = extract_json_block(raw_output)
        explanation = extract_explanation_block(raw_output)

        logger.info("\n📄 JSON Output:\n" + "-" * 50 + f"\n{json.dumps(json_data, indent=2)}\n")
        logger.info("\n🧠 Explanation:\n" + "-" * 50 + f"\n{explanation}\n")

        print("\n📄 JSON Output:\n" + "-" * 50)
        print(json.dumps(json_data, indent=2))
        print("\n🧠 Explanation:\n" + "-" * 50)
        print(explanation)

        logger.info("Parsing and validating JSON...")

        # Validate only the inner `slo` block
        slo_block = json_data.get("slo")
        if not slo_block:
            raise ValueError("Missing 'slo' key in response")

        is_valid, errors = validate_slo_json(slo_block)
        if not is_valid:
            logger.error(f"❌ JSON validation failed: {errors}")
            raise ValueError(f"SLO JSON is invalid: {errors}")

        # Optionally attach explanation
        if explain:
            json_data["explanation"] = explanation.strip()

        # Write full object to output
        with open(output_path, "w") as f:
            json.dump(json_data, f, indent=2)

        logger.info(f"✅ SLO JSON written to {output_path}")

    except Exception as e:
        logger.error(f"❌ Error during SLO generation: {e}")
        raise

def extract_json_block(text: str) -> dict:
    """Extract and parse the first complete JSON object in the text."""
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
    """Extract the explanation block following the 'explanation' key."""
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