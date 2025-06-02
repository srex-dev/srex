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
                    "required": True,
                },
                "threshold": {
                    "type": ["float", "integer"],
                    "required": True,
                    "coerce": float,
                },
            },
        },
    },

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
                    "type": "string",
                    "required": True,
                    "regex": r"^\d+(\.\d+)?$",  # Ensure numeric targets
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


def validate_slo_yaml(data: dict) -> tuple[bool, dict]:
    v = Validator(slo_schema, allow_unknown=False)  # Turn off unknown fields
    is_valid = v.validate(data)
    return is_valid, v.errors if not is_valid else {}