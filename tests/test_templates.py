import json
import os
from pathlib import Path
import pytest
from jinja2 import Environment, FileSystemLoader
from core.schema.models import ServiceInput, OutputSchema
from core.schema import validate_input, validate_output

# Setup Jinja2 environment
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

def load_example_data(filename):
    """Load example data from the examples directory."""
    example_path = Path(__file__).parent.parent / "examples" / filename
    with open(example_path) as f:
        return json.load(f)

def test_sli_generation_template():
    """Test SLI generation template processing."""
    template = env.get_template("sli_generation.j2")
    input_data = load_example_data("sli_generation_input.json")
    
    # Validate input data
    assert validate_input(input_data)
    
    # Process template
    prompt = template.render(**input_data)
    
    # Basic validation of generated prompt
    assert "payment-service" in prompt
    assert "microservice" in prompt
    assert "high" in prompt
    assert "payment-api" in prompt
    assert "payment-db" in prompt
    
    # Load expected output
    expected_output = load_example_data("sli_generation_output.json")
    
    # Validate output schema
    assert validate_output(expected_output)
    
    # Check key fields
    assert "slis" in expected_output
    assert len(expected_output["slis"]) > 0
    assert all("name" in sli for sli in expected_output["slis"])
    assert all("type" in sli for sli in expected_output["slis"])
    assert all("thresholds" in sli for sli in expected_output["slis"])

def test_slo_generation_template():
    """Test SLO generation template processing."""
    template = env.get_template("slo_generation.j2")
    input_data = load_example_data("slo_generation_input.json")
    
    # Validate input data
    assert validate_input(input_data)
    
    # Process template
    prompt = template.render(**input_data)
    
    # Basic validation of generated prompt
    assert "payment-service" in prompt
    assert "PCI-DSS" in prompt
    assert "GDPR" in prompt
    assert "error_budget" in prompt
    
    # Load expected output
    expected_output = load_example_data("slo_generation_output.json")
    
    # Validate output schema
    assert validate_output(expected_output)
    
    # Check key fields
    assert "slos" in expected_output
    assert len(expected_output["slos"]) > 0
    assert all("name" in slo for slo in expected_output["slos"])
    assert all("target" in slo for slo in expected_output["slos"])
    assert all("error_budget" in slo for slo in expected_output["slos"])

def test_alert_generation_template():
    """Test alert generation template processing."""
    template = env.get_template("alert_generation.j2")
    input_data = load_example_data("alert_generation_input.json")
    
    # Validate input data
    assert validate_input(input_data)
    
    # Process template
    prompt = template.render(**input_data)
    
    # Basic validation of generated prompt
    assert "payment-service" in prompt
    assert "critical" in prompt
    assert "warning" in prompt
    assert "pagerduty" in prompt
    
    # Load expected output
    expected_output = load_example_data("alert_generation_output.json")
    
    # Validate output schema
    assert validate_output(expected_output)
    
    # Check key fields
    assert "alerts" in expected_output
    assert len(expected_output["alerts"]) > 0
    assert all("name" in alert for alert in expected_output["alerts"])
    assert all("severity" in alert for alert in expected_output["alerts"])
    assert all("notifications" in alert for alert in expected_output["alerts"])

def test_analysis_template():
    """Test analysis template processing."""
    template = env.get_template("analysis.j2")
    input_data = load_example_data("analysis_input.json")
    
    # Validate input data
    assert validate_input(input_data)
    
    # Process template
    prompt = template.render(**input_data)
    
    # Basic validation of generated prompt
    assert "payment-service" in prompt
    assert "current_state" in prompt
    assert "recommendations" in prompt
    assert "risks" in prompt
    
    # Load expected output
    expected_output = load_example_data("analysis_output.json")
    
    # Validate output schema
    assert validate_output(expected_output)
    
    # Check key fields
    assert "current_state" in expected_output
    assert "recommendations" in expected_output
    assert "risks" in expected_output
    assert len(expected_output["recommendations"]) > 0
    assert len(expected_output["risks"]) > 0

def test_runbook_template():
    """Test runbook template processing."""
    template = env.get_template("runbook.j2")
    input_data = load_example_data("runbook_input.json")
    
    # Validate input data
    assert validate_input(input_data)
    
    # Process template
    prompt = template.render(**input_data)
    
    # Basic validation of generated prompt
    assert "payment-service" in prompt
    assert "investigation" in prompt
    assert "resolution" in prompt
    assert "escalation" in prompt
    
    # Load expected output
    expected_output = load_example_data("runbook_output.json")
    
    # Validate output schema
    assert validate_output(expected_output)
    
    # Check key fields
    assert "runbooks" in expected_output
    assert len(expected_output["runbooks"]) > 0
    assert all("investigation" in runbook for runbook in expected_output["runbooks"])
    assert all("resolution" in runbook for runbook in expected_output["runbooks"])
    assert all("escalation" in runbook for runbook in expected_output["runbooks"])

def test_template_integration():
    """Test the integration between templates."""
    # Load all example data
    sli_input = load_example_data("sli_generation_input.json")
    slo_input = load_example_data("slo_generation_input.json")
    alert_input = load_example_data("alert_generation_input.json")
    analysis_input = load_example_data("analysis_input.json")
    runbook_input = load_example_data("runbook_input.json")
    
    # Verify service consistency
    service_name = sli_input["service_name"]
    assert slo_input["service_name"] == service_name
    assert alert_input["service_name"] == service_name
    assert analysis_input["service_name"] == service_name
    assert runbook_input["service_name"] == service_name
    
    # Verify component consistency
    components = [sli["component"] for sli in sli_input["sli_inputs"]]
    slo_components = [sli["component"] for sli in slo_input["sli_inputs"]]
    alert_components = [sli["component"] for sli in alert_input["sli_inputs"]]
    assert all(comp in slo_components for comp in components)
    assert all(comp in alert_components for comp in components)
    
    # Verify metadata consistency
    for sli in sli_input["sli_inputs"]:
        if "metadata" in sli:
            assert "business_impact" in sli["metadata"]
            assert "requirements" in sli["metadata"] 