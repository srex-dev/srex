# cli/test_sli_input.py

import sys
import json
from pathlib import Path
from cerberus import Validator
from core.input_schema.sli import sli_input_schema
from core.logger import logger


def validate_sli_input(file_path: str) -> bool:
    path = Path(file_path)
    if not path.exists():
        logger.error(f"❌ File not found: {file_path}")
        return False

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to parse JSON: {e}")
        return False

    validator = Validator(sli_input_schema)
    if validator.validate(data):
        logger.info("✅ SLI input is valid.")
        return True
    else:
        logger.error("❌ SLI input validation failed:")
        for field, errors in validator.errors.items():
            logger.error(f" - {field}: {errors}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cli/test_sli_input.py path/to/availability.json")
        sys.exit(1)

    input_file = sys.argv[1]
    result = validate_sli_input(input_file)
    sys.exit(0 if result else 1)