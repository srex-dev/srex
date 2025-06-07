# core/output_schema.py

from cerberus import Validator

# === SREX OUTPUT SCHEMAS ===

srex_output_schema = {
    "sli": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string"},
                "type": {
                    "type": "string",
                    "allowed": ["availability", "latency", "error_rate"]
                },
                "unit": {"type": "string"},
                "source": {"type": "string"},
                "metric": {"type": "string"}
            }
        },
        "required": True
    },
    "alerts": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string"},
                "severity": {
                    "type": "string",
                    "allowed": ["info", "warning", "critical"]
                },
                "expr": {"type": "string"},
                "for": {"type": "string"}
            }
        },
        "required": True
    },
    "explanation": {"type": "string"},
    "llm_suggestions": {
        "type": "list",
        "schema": {"type": "string"}
    }
}

# === SCHEMA TYPES MAPPED TO CONTEXT ===

SCHEMA_TYPES = {
    "slo": srex_output_schema,
    "availability": srex_output_schema,
    "automation": srex_output_schema,
    "observability": srex_output_schema,
    "alerting": srex_output_schema,
    "reliability": srex_output_schema
}

# === VALIDATION FUNCTION ===

def validate_srex_output(data, schema_type="slo"):
    schema = SCHEMA_TYPES.get(schema_type)
    if not schema:
        raise ValueError(f"Unknown schema type: {schema_type}")

    validator = Validator(schema)
    is_valid = validator.validate(data)
    return is_valid, validator.errors