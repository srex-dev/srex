from cerberus import Validator

slo_schema = {
    "service_name": {"type": "string", "required": True},
    "description": {"type": "string", "required": False},
    "objectives": {
        "type": "list",
        "required": True,
        "minlength": 1,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "sli": {"type": "string", "required": True},
                "target": {
                    "type": ["float", "integer"],
                    "required": True,
                },
                "time_window": {"type": "string", "required": True},
            },
        },
    },
    "explanation": {
        "type": "string",
        "required": False
    },
}

sli_schema = {
    "sli": {
        "type": "list",
        "required": True,
        "minlength": 1,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "type": {
                    "type": "string",
                    "allowed": ["latency", "error", "availability", "throughput", "queue"],
                    "required": True,
                },
                "unit": {"type": "string", "required": True},
                "source": {"type": "string", "required": True},
                "metric": {"type": "string", "required": True},
            }
        }
    },
    "explanation": {
        "type": "string",
        "required": False
    }
}

def validate_slo_json(data: dict) -> tuple[bool, dict]:
    # Support nested LLM output with "slo" and "explanation"
    slo_data = data.get("slo", data)  # fallback to root if "slo" is missing

    v = Validator(slo_schema, allow_unknown=False)
    is_valid = v.validate(slo_data)
    return is_valid, v.errors if not is_valid else {}

def validate_sli_json(data: dict) -> tuple[bool, dict]:
    v = Validator(sli_schema, allow_unknown=False)
    is_valid = v.validate(data)
    return is_valid, v.errors if not is_valid else {}