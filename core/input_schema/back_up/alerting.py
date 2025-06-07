alerting_context_schema = {
    "service_name": {"type": "string", "required": True},
    "description": {"type": "string", "required": False},
    "metrics": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "type": {"type": "string", "allowed": ["latency", "error", "utilization", "availability", "custom"], "required": True},
                "source": {"type": "string", "required": True}
            }
        }
    }
}
