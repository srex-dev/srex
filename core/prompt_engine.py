import json
import textwrap
from pathlib import Path
from llm.interface import call_llm
from core.logger import logger
from core.output_schema import validate_srex_output


def generate_prompt_response(input_json: dict, template='default', explain=True, model='ollama', schema_type=None) -> dict:
    try:
        template_path = Path(template) if Path(template).is_file() else Path("prompt_templates") / f"{template}.txt"
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        logger.info(f"📨 Using template: {template_path}")
        prompt_template = template_path.read_text()
        prompt = prompt_template.replace("{input}", json.dumps(input_json, indent=2))

        logger.info(f"📤 Sending prompt to LLM (provider={model})...")
        raw_output = call_llm(prompt, explain=explain, model=model)
        logger.info("✅ LLM response received successfully.")

        json_data = extract_json_block(raw_output)

        if explain and not json_data.get("explanation"):
            logger.warning("⚠️ Raw LLM output:\n" + raw_output)
            json_data["explanation"] = extract_explanation_block(raw_output).strip()

        # ✅ Pass schema_type explicitly to validation
        logger.info("🔍 Validating JSON with `validate_srex_output`...")
        logger.info(f"🔧 Validating with schema_type={schema_type}")

        is_valid, validation_error = validate_srex_output(json_data, schema_type=schema_type)


        if not is_valid:
            raise ValueError(f"Output JSON is invalid: {validation_error}")

        return json_data

    except Exception as e:
        logger.error(f"❌ Error during prompt generation: {e}")
        raise

def generate_definitions(input_path: str, output_path: str, template: str, explain: bool, model: str, show_suggestions: bool = True):
    """
    CLI wrapper to load input from file and write output to file.
    """
    try:
        logger.info(f"📥 Loading input file: {input_path}")
        input_data = Path(input_path).read_text()
        input_json = json.loads(input_data)

        json_data = generate_prompt_response(
            input_json,
            template=template,
            explain=explain,
            model=model,
            schema_type=template  # ✅ Ensures correct schema validation
        )

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
        text = text.replace("```json", "").replace("```", "").strip()

        start = text.find('{')
        if start == -1:
            raise ValueError("No JSON object found")

        brace_count = 0
        for i, c in enumerate(text[start:], start=start):
            if c == '{':
                brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        else:
            raise ValueError("JSON block not closed properly")

        json_str = text[start:end]

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Escape backslashes and quotes intelligently
            sanitized = (
                json_str.replace('\\', '\\\\')    # double all backslashes
                         .replace('\\"', '"')     # remove escaped double-quotes
                         .replace('"\n', '"')     # trim broken strings
            )
            return json.loads(sanitized)

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