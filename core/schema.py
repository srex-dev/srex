from cerberus import Validator

slo_schema = {
    "service_name": {"type": "string", "required": True},
    "description": {"type": "string", "required": False},
    "indicators": {
        "type": "list",
        "required": False,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "type": {
                    "type": "string",
                    "allowed": ["latency", "error", "availability", "throughput"],
                    "required": True
                },
                "threshold": {"type": "float", "required": True},
            },
        },
    },
    "objectives": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "sli": {"type": "string", "required": True},
                "target": {"type": "string", "required": True},
                "time_window": {"type": "string", "required": True},
            },
        },
    },
    "explanation": {"type": "string", "required": False},  # Optional LLM commentary
}


def validate_slo_yaml(data: dict) -> tuple[bool, dict]:
    v = Validator(slo_schema)
    is_valid = v.validate(data)
    return is_valid, v.errors if not is_valid else {}