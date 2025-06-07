# core/basic_validator.py

from typing import Dict

def basic_output_shape_check(data: Dict, required_keys: list) -> Dict[str, str]:
    """
    Checks if the required top-level keys exist and are of expected types (loosely).

    Args:
        data (Dict): JSON object to validate.
        required_keys (list): Expected top-level keys.

    Returns:
        Dict[str, str]: Any missing or incorrectly typed keys with error messages.
    """
    errors = {}

    for key in required_keys:
        if key not in data:
            errors[key] = "Missing required top-level key"
        else:
            if key in ["sli", "slo", "alerts", "llm_suggestions"] and not isinstance(data[key], list):
                errors[key] = "Must be a list"
            elif key == "explanation" and not isinstance(data[key], str):
                errors[key] = "Must be a string"

    return errors