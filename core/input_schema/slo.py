slo_context_schema = {
    "service_name": {"type": "string", "required": True},
    "metrics": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "component": {"type": "string"},
                "availability_target": {"type": "float"},
                "latency_target_ms": {"type": "integer"}
            }
        }
    }
}