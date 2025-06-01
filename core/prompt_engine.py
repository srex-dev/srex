import yaml
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

        # Split YAML and explanation
        yaml_part, explanation = split_yaml_and_explanation(raw_output)

        logger.info("Parsing LLM output YAML...")
        parsed_yaml = yaml.safe_load(yaml_part)

        if explain:
            parsed_yaml["explanation"] = explanation.strip()

        is_valid, errors = validate_slo_yaml(parsed_yaml)
        if not is_valid:
            logger.error(f"❌ YAML validation failed: {errors}")
            raise ValueError(f"SLO YAML is invalid: {errors}")

        with open(output_path, "w") as f:
            yaml.dump(parsed_yaml, f)

        logger.info(f"✅ SLO YAML written to {output_path}")
    except Exception as e:
        logger.error(f"❌ Error during SLO generation: {e}")
        raise

def split_yaml_and_explanation(text: str) -> tuple[str, str]:
    """
    Tries to split YAML from LLM explanation.
    Assumes explanation follows the YAML after a blank line or `---` separator.
    """
    parts = text.strip().split("\n\n", 1)
    if len(parts) == 2:
        yaml_part, explanation = parts
    else:
        yaml_part = text
        explanation = ""

    # Handle triple backticks or other markdown formatting if present
    yaml_part = yaml_part.replace("```yaml", "").replace("```", "").strip()
    explanation = explanation.replace("```", "").strip()

    return yaml_part, explanation