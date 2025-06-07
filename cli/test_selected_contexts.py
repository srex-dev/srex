import json
import pytest
from pathlib import Path
from cerberus import Validator

from core.prompt_engine import generate_prompt_response
from core.schema_validator import validate_srex_output
from core.input_schema import (
    automation_context_schema,
    availability_context_schema,
    observability_context_schema,
    alerting_context_schema,
    reliability_context_schema,
    slo_context_schema
)

BASE_DIR = Path(__file__).resolve().parent.parent
CONTEXT_DIR = BASE_DIR / "examples" / "context-variants"
TEMPLATE_DIR = BASE_DIR / "core" / "prompt_templates"

CONTEXT_CONFIGS = {
    "automation": {
        "schema": automation_context_schema,
        "filename": "automation.json",
        "template": "automation"
    },
    "availability": {
        "schema": availability_context_schema,
        "filename": "availability.json",
        "template": "availability"
    },
    "observability": {
        "schema": observability_context_schema,
        "filename": "observability.json",
        "template": "observability"
    },
    "alerting": {
        "schema": alerting_context_schema,
        "filename": "alerting.json",
        "template": "alerting"
    },
    "reliability": {
        "schema": reliability_context_schema,
        "filename": "reliability.json",
        "template": "reliability"
    },
    "slo": {
        "schema": slo_context_schema,
        "filename": "slo.json",
        "template": "slo"
    }
}

@pytest.mark.parametrize("context_key", list(CONTEXT_CONFIGS.keys()))
def test_context_generation_and_validation(context_key):
    config = CONTEXT_CONFIGS[context_key]
    context_path = CONTEXT_DIR / config["filename"]
    template_path = TEMPLATE_DIR / f"{config['template']}.j2"

    assert context_path.exists(), f"Missing context file: {context_path}"
    assert template_path.exists(), f"Missing template: {template_path}"

    with context_path.open() as f:
        data = json.load(f)

    validator = Validator(config["schema"])
    assert validator.validate(data), f"Input schema validation failed: {validator.errors}"

    result = generate_prompt_response(
        input_json=data,
        template=config["template"]
    )

    valid_output, output_errors = validate_srex_output(result, schema_type=context_key)
    assert valid_output, f"Output schema validation failed: {output_errors}"