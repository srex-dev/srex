automation_output_schema = {
    "slo": {
        "type": "list",
        "schema": {"type": "dict"},
        "required": True
    },
    "sli": {
        "type": "list",
        "schema": {"type": "dict"},
        "required": True
    },
    "alerts": {
        "type": "list",
        "schema": {"type": "dict"},
        "required": True
    },
    "explanation": {"type": "string", "required": True},
    "llm_suggestions": {
        "type": "list",
        "schema": {"type": "string"},
        "required": False
    }
}