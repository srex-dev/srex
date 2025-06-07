availability_context_schema = {
    "service_name": {"type": "string", "required": True},
    "environment": {"type": "string", "required": True},
    "service": {"type": "string", "required": True},
    "metrics": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "type": {"type": "string"},
                "name": {"type": "string"},
                "source": {"type": "string"}
            }
        }
    }
}