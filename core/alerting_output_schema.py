alerting_output_schema = {
    "alerts": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "severity": {
                    "type": "string",
                    "required": True,
                    "allowed": ["info", "warning", "critical"]
                },
                "expr": {"type": "string", "required": True},
                "for": {"type": "string", "required": True}
            }
        }
    },
    "explanation": {"type": "string", "required": True},
    "llm_suggestions": {"type": "list", "schema": {"type": "string"}, "required": False}
}