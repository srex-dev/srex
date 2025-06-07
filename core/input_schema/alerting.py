alerting_context_schema = {
    "service_name": {"type": "string", "required": True},
    "metrics": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string"},
                "expr": {"type": "string"},
                "severity": {"type": "string"},
                "for": {"type": "string"}
            }
        }
    }
}