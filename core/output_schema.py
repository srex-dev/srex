# backend/core/output_schema.py

from cerberus import Validator

# === SREX OUTPUT SCHEMAS ===

srex_output_schema = {
    "sli": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True, "empty": False},
                "description": {"type": "string"},
                "type": {
                    "type": "string",
                    "allowed": ["availability", "latency", "error", "throughput", "queue", "saturation", "utilization", "custom"],
                    "required": True
                },
                "unit": {"type": "string"},
                "source": {"type": "string"},
                "metric": {"type": "string"},
                "value": {"type": ["string", "integer", "float"]}
            }
        }
    },
    "slo": {
        "type": "list",
        "required": True,
        "default": [],
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True, "empty": False},
                "description": {"type": "string"},
                "sli": {"type": "string", "required": True},
                "target": {"type": "float", "required": True},
                "time_window": {
                    "type": "string",
                    "allowed": ["7d", "30d", "90d"],
                    "required": True
                }
            }
        }
    },
    "alerts": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True, "empty": False, "default": "unnamed-alert"},
                "description": {"type": "string"},
                "severity": {
                    "type": "string",
                    "allowed": ["info", "warning", "critical"]
                },
                "expr": {"type": "string"},
                "for": {"type": "string"},
                "threshold": {"type": ["string", "integer", "float"]},
                "duration": {"type": ["string", "integer", "float"]}
            }
        }
    },
    "explanation": {
        "type": "string",
        "minlength": 10,
        "required": True
    },
    "llm_suggestions": {
        "type": "list",
        "required": True,
        "minlength": 1,
        "schema": {
            "type": "dict",
            "allow_unknown": True  # Allow any fields in the suggestion objects
        }
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