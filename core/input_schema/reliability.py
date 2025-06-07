reliability_context_schema = {
    "service_name": {"type": "string", "required": True},
    "metrics": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "unit": {"type": "string"},
                "source": {"type": "string"}
            }
        }
    }
}