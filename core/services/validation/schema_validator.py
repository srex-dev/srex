from cerberus import Validator
from backend.core.output_schema import srex_output_schema

SCHEMA_TYPES = {
    "slo": srex_output_schema,
    "availability": srex_output_schema,
    "automation": srex_output_schema,
    "observability": srex_output_schema,
    "alerting": srex_output_schema,
    "reliability": srex_output_schema,
}

def validate_srex_output(data, schema_type="slo"):
    schema = SCHEMA_TYPES.get(schema_type)
    if not schema:
        raise ValueError(f"Unknown schema type: {schema_type}")

    validator = Validator(schema)
    is_valid = validator.validate(data)
    return is_valid, validator.errors