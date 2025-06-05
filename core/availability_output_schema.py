# core/output_schema/availability_output_schema.py

availability_output_schema = {
    "slo": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "sli": {"type": "string", "required": True},
                "target": {"type": "float", "required": True},
                "time_window": {"type": "string", "required": True}
            }
        },
        "required": True
    },
    "sli": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "type": {"type": "string", "allowed": ["availability"], "required": True},
                "unit": {"type": "string", "required": True},
                "source": {"type": "string", "required": True},
                "metric": {"type": "string", "required": True}
            }
        },
        "required": True
    },
    "explanation": {"type": "string", "required": True},
    "llm_suggestions": {"type": "list", "schema": {"type": "string"}, "required": False}
}