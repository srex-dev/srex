from cerberus import Validator

observability_context_schema = {
    "service_name": {"type": "string", "required": True},
    "description": {"type": "string", "required": True},
    "metrics": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "type": {"type": "string", "required": True},
                "source": {"type": "string", "required": True}
            }
        },
        "required": True
    }
}
sli_context_schema = {
    "service_name": {"type": "string", "required": True},
    "description": {"type": "string", "required": True},
    "sli": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "type": {"type": "string", "required": True},
                "unit": {"type": "string", "required": True},
                "source": {"type": "string", "required": True},
                "metric": {"type": "string", "required": True}
            }
        },
        "required": True
    }
}

availability_context_schema = {
    "service_name": {"type": "string", "required": True},
    "objectives": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "availability_target": {"type": "float", "min": 0.0, "max": 1.0, "required": True},
                "component": {"type": "string", "required": True},
                "comment": {"type": "string", "required": False}
            }
        }
    }
}

alerting_context_schema = {
    "alerts": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "expr": {"type": "string", "required": True},
                "severity": {"type": "string", "allowed": ["info", "warning", "critical"], "required": True},
                "for": {"type": "string", "required": True},
                "description": {"type": "string", "required": True}
            }
        },
        "required": True
    }
}

reliability_context_schema = {
    "service_name": {"type": "string", "required": True},
    "reliability_targets": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "metric": {"type": "string", "required": True},
                "goal": {"type": "float", "min": 0.0, "max": 1.0, "required": True},
                "comment": {"type": "string", "required": False}
            }
        },
        "required": True
    }
}
automation_context_schema = {
    "service_name": {"type": "string", "required": True},
    "description": {"type": "string", "required": True},
    "automation_tasks": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "trigger": {"type": "string", "required": True},
                "action": {"type": "string", "required": True},
                "rollback": {"type": "string", "required": False},
                "severity": {
                    "type": "string",
                    "required": False,
                    "allowed": ["low", "medium", "high"]
                }
            }
        }
    }
}
frontend_web_app_context_schema = {
    "app_name": {"type": "string", "required": True},
    "user_journeys": {
        "type": "list",
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "description": {"type": "string", "required": True},
                "impact": {"type": "string", "required": True}
            }
        },
        "required": True
    }
}