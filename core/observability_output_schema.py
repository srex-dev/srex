observability_output_schema = {
    "sli": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "type": {
                    "type": "string",
                    "required": True,
                    "allowed": ["latency", "error", "availability", "throughput", "queue", "saturation", "utilization", "custom"]
                },
                "unit": {"type": "string", "required": True},
                "source": {"type": "string", "required": True},
                "metric": {"type": "string", "required": True}
            }
        }
    },
    "explanation": {"type": "string", "required": True},
    "llm_suggestions": {"type": "list", "schema": {"type": "string"}, "required": False}
}