# core/output_schema.py

from cerberus import Validator



# Import each schema from its dedicated file
from core.availability_output_schema import availability_output_schema
from core.automation_output_schema import automation_output_schema
from core.observability_output_schema import observability_output_schema
from core.alerting_output_schema import alerting_output_schema
from core.reliability_output_schema import reliability_output_schema


# === Schema Dispatcher ===

SCHEMA_DISPATCH = {
    "observability": observability_output_schema,
    "availability": availability_output_schema,
    "alerting": alerting_output_schema,
    "reliability": reliability_output_schema,
    "automation": automation_output_schema,
}

# === Validation Function ===

def validate_srex_output(data: dict, schema_type: str = None):
    """
    Validates output data using the correct schema based on `schema_type`.

    Args:
        data (dict): The LLM-generated output JSON.
        schema_type (str): The type of schema to validate against (e.g., 'observability', 'alerting').

    Returns:
        (bool, dict or str): Tuple of validation success flag and error details (if any).
    """
    if not schema_type:
        return False, "Missing `schema_type` for output validation."

    schema = SCHEMA_DISPATCH.get(schema_type)
    if not schema:
        return False, f"No output schema defined for type: {schema_type}"

    validator = Validator(schema)
    if not validator.validate(data):
        return False, validator.errors

    return True, None
