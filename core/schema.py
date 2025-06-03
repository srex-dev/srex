from cerberus import Validator

# --- SLO Schema ---
slo_schema = {
    "service_name": {"type": "string", "required": True},
    "description": {"type": "string", "required": False},
    "objectives": {
        "type": "list",
        "required": True,
        "minlength": 1,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "sli": {"type": "string", "required": True},
                "target": {
                    "type": ["float", "integer"],
                    "required": True,
                },
                "time_window": {"type": "string", "required": True},
            },
        },
    },
    "explanation": {
        "type": "string",
        "required": False
    },
}

# --- SLI Schema ---
sli_schema = {
    "sli": {
        "type": "list",
        "required": True,
        "minlength": 1,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "type": {
                    "type": "string",
                    "allowed": [
                        "latency",
                        "error",
                        "availability",
                        "throughput",
                        "queue",
                        "saturation",
                        "utilization",
                        "custom"
                    ],
                    "required": True,
                },
                "unit": {"type": "string", "required": True},
                "source": {
                    "type": "string",
                    "allowed": [
                        "prometheus",
                        "datadog",
                        "newrelic",
                        "cloudwatch",
                        "stackdriver",
                        "grafana",
                        "custom"
                    ],
                    "required": True
                },
                "metric": {"type": "string", "required": True},
            }
        }
    },
    "explanation": {
        "type": "string",
        "required": False
    }
}
alert_schema = {
    "alerts": {
        "type": "list",
        "required": True,
        "minlength": 1,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "expr": {"type": "string", "required": True},  # PromQL or other rule
                "for": {"type": "string", "required": True},   # e.g., "5m"
                "severity": {
                    "type": "string",
                    "allowed": ["critical", "warning", "info"],
                    "required": True
                },
                "labels": {
                    "type": "dict",
                    "required": False,
                    "schema": {"type": "string"}
                },
                "annotations": {
                    "type": "dict",
                    "required": False,
                    "schema": {"type": "string"}
                }
            }
        }
    },
    "explanation": {
        "type": "string",
        "required": False
    }
}
# --- Validators ---
def validate_slo_json(data: dict) -> tuple[bool, dict]:
    slo_data = data.get("slo", data)
    v = Validator(slo_schema, allow_unknown=False)
    is_valid = v.validate(slo_data)
    return is_valid, v.errors if not is_valid else {}

def validate_sli_json(data: dict) -> tuple[bool, dict]:
    v = Validator(sli_schema, allow_unknown=False)
    is_valid = v.validate(data)
    return is_valid, v.errors if not is_valid else {}

def validate_alert_json(data: dict) -> tuple[bool, dict]:
    v = Validator(alert_schema, allow_unknown=False)
    is_valid = v.validate(data)
    return is_valid, v.errors if not is_valid else {}