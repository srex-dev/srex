reliability_output_schema = {
    "sli": {
        "type": "list",
        "required": True,
        "schema": {"type": "dict"}
    },
    "slo": {
        "type": "list",
        "required": True,
        "schema": {"type": "dict"}
    },
    "alerts": {
        "type": "list",
        "required": True,
        "schema": {"type": "dict"}
    },
    "explanation": {"type": "string", "required": True},
    "llm_suggestions": {"type": "list", "schema": {"type": "string"}, "required": False}
}