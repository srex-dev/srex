import pytest
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from core.schema import validate_input, validate_output
from llm.interface import call_llm

@pytest.fixture
def template_env():
    """Create a Jinja2 environment for templates."""
    template_dir = Path(__file__).parent.parent / "templates"
    return Environment(loader=FileSystemLoader(str(template_dir)))

@pytest.fixture
def example_data():
    """Load all example data."""
    example_dir = Path(__file__).parent.parent / "examples"
    data = {}
    for file in example_dir.glob("*_input.json"):
        with open(file) as f:
            data[file.stem.replace("_input", "")] = json.load(f)
    return data

@pytest.fixture
def expected_outputs():
    """Load all expected outputs."""
    example_dir = Path(__file__).parent.parent / "examples"
    data = {}
    for file in example_dir.glob("*_output.json"):
        with open(file) as f:
            data[file.stem.replace("_output", "")] = json.load(f)
    return data

@pytest.fixture
def mock_llm_response(monkeypatch):
    """Mock LLM responses for testing."""
    def mock_call_llm(prompt):
        # Extract template name from prompt
        template_name = None
        if "SLI generation" in prompt:
            template_name = "sli"
        elif "SLO generation" in prompt:
            template_name = "slo"
        elif "alert generation" in prompt:
            template_name = "alert"
        elif "service analysis" in prompt:
            template_name = "analysis"
        elif "runbook" in prompt:
            template_name = "runbook"
        
        # Load corresponding expected output
        if template_name:
            output_path = Path(__file__).parent.parent / "examples" / f"{template_name}_generation_output.json"
            with open(output_path) as f:
                return json.dumps(json.load(f))
        return "{}"
    
    monkeypatch.setattr("llm.interface.call_llm", mock_call_llm)
    return mock_call_llm

@pytest.fixture
def validate_schema():
    """Validate schema for input and output."""
    def validate(data, is_input=True):
        if is_input:
            return validate_input(data)
        return validate_output(data)
    return validate 