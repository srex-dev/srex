observability_context_schema = {
    "service": {"type": "string", "required": True},
    "environment": {"type": "string", "required": True},
    "sli": {
        "type": "dict",
        "required": True
    },
    "objectives": {
        "type": "dict",
        "required": False
    }
}
