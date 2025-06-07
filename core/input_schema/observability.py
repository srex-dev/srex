observability_context_schema = {
    "environment": {"type": "string", "required": True},
    "service": {"type": "string", "required": True},
    "sli": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "source": {"type": "string"}
            }
        }
    }
}