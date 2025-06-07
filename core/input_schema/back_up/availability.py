availability_context_schema = {
    "service_name": {"type": "string", "required": True},
    "objectives": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "availability_target": {"type": "float", "required": True},
                "component": {"type": "string", "required": True},
                "comment": {"type": "string", "required": False}
            }
        }
    }
}
