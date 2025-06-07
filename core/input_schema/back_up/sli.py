# core/input_schema/sli.py

sli_input_schema = {
    "service_name": {
        "type": "string",
        "required": True,
        "empty": False
    },
    "objectives": {
        "type": "list",
        "required": True,
        "minlength": 1,
        "schema": {
            "type": "dict",
            "schema": {
                "component": {"type": "string", "required": True, "empty": False},
                "availability_target": {"type": "string", "required": True},  # could be changed to float
                "comment": {"type": "string", "required": False},
                "sli_type": {"type": "string", "required": False, "default": "availability"}
            }
        }
    },
    "live_sli_data": {
        "type": "list",
        "required": False,
        "schema": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True},
                "value": {"type": "float", "required": True},
                "unit": {"type": "string", "required": True},
                "source": {"type": "string", "required": True},
                "timestamp": {"type": "integer", "required": True}
            }
        }
    }
}