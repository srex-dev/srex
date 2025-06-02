import yaml
import re
import textwrap
from pathlib import Path
from core.schema import validate_slo_yaml
from llm.interface import call_llm
from core.logger import logger

def generate_slo_definitions(input_path: str, output_path: str, template: str, explain: bool, provider: str = "ollama"):
    try:
        logger.info(f"Loading input file: {input_path}")
        input_data = Path(input_path).read_text()

        template_path = f"prompt_templates/{template}.txt"
        logger.info(f"Using template: {template_path}")
        prompt_template = Path(template_path).read_text()
        prompt = prompt_template.replace("{input}", input_data)

        logger.info(f"Sending prompt to LLM ({provider})...")
        raw_output = call_llm(prompt, explain=explain)
        logger.info("✅ LLM response received successfully.")

        yaml_text = extract_yaml_block(raw_output)
        explanation = extract_explanation_block(raw_output)

        import sys
        logger.info("\n📄 YAML Output:\n" + "-"*50 + f"\n{yaml_text}\n")
        logger.info("\n🧠 Explanation:\n" + "-"*50 + f"\n{explanation}\n")
        sys.stdout.write("\n📄 YAML Output:\n" + "-"*50 + "\n")
        sys.stdout.write(yaml_text + "\n")
        sys.stdout.write("\n🧠 Explanation:\n" + "-"*50 + "\n")
        sys.stdout.write(explanation + "\n")
        sys.stdout.flush()

        logger.info("Parsing LLM output YAML...")
        parsed_yaml = yaml.safe_load(yaml_text)

        if explain and isinstance(parsed_yaml, dict):
            parsed_yaml["explanation"] = explanation.strip()

        is_valid, errors = validate_slo_yaml(parsed_yaml)
        if not is_valid:
            logger.error(f"❌ YAML validation failed: {errors}")
            raise ValueError(f"SLO YAML is invalid: {errors}")

        with open(output_path, "w") as f:
            yaml.dump(parsed_yaml, f, sort_keys=False)

        logger.info(f"✅ SLO YAML written to {output_path}")
    except Exception as e:
        logger.error(f"❌ Error during SLO generation: {e}")
        raise


def extract_yaml_block(text: str) -> str:
    import unicodedata

    # Remove code fences and dedent
    cleaned = text.replace("```yaml", "").replace("```", "")
    cleaned = textwrap.dedent(cleaned)

    # Normalize unicode spaces (e.g. non-breaking spaces)
    cleaned = unicodedata.normalize("NFKC", cleaned)

    # Remove Windows line endings
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

    # Split off explanation if present
    yaml_lines = []
    for line in cleaned.splitlines():
        if line.strip().lower().startswith("explanation:"):
            break
        yaml_lines.append(line)

    yaml_text = "\n".join(yaml_lines).strip()

    # Fix bad indentation (optional: use regex cautiously)
    yaml_text = re.sub(r"^\s{6}", "  ", yaml_text, flags=re.MULTILINE)

    # Validate parseability before returning
    try:
        yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        raise ValueError(f"❌ Error parsing YAML block: {e}")

    return yaml_text


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