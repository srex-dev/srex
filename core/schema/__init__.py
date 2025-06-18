from .base import SchemaRegistry, PydanticValidator
from .models import ServiceInput, OutputSchema

# Register input schema
SchemaRegistry.register_validator(
    "input",
    PydanticValidator(ServiceInput)
)

# Register output schema
SchemaRegistry.register_validator(
    "output",
    PydanticValidator(OutputSchema)
)

def validate_input(data: dict) -> bool:
    """Validate input data."""
    return SchemaRegistry.validate("input", data)

def validate_output(data: dict) -> bool:
    """Validate output data."""
    return SchemaRegistry.validate("output", data)

def get_input_errors() -> list[str]:
    """Get input validation errors."""
    return SchemaRegistry.get_errors("input")

def get_output_errors() -> list[str]:
    """Get output validation errors."""
    return SchemaRegistry.get_errors("output")

def get_input_schema() -> dict:
    """Get input schema definition."""
    return SchemaRegistry.get_schema("input")

def get_output_schema() -> dict:
    """Get output schema definition."""
    return SchemaRegistry.get_schema("output") 