automation_context_schema = {
    "service_name": {"type": "string", "required": True},
    "automation_goals": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "component": {"type": "string", "required": True},
                "goal": {"type": "string", "required": True},
                "tools": {
                    "type": "list",
                    "schema": {"type": "string"}
                }
            }
        }
    }
}