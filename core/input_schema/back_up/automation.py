automation_context_schema = {
    "service_name": {"type": "string", "required": True},
    "description": {"type": "string", "required": False},
    "automation_tools": {"type": "list", "schema": {"type": "string"}, "required": True},
    "metrics": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "type": {"type": "string", "required": True},
                "source": {"type": "string", "required": True}
            }
        }
    }
}
