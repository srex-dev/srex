import json
import os
from pathlib import Path
import pytest
from jinja2 import Environment, FileSystemLoader
from core.schema import validate_output
from llm.interface import call_llm

# Setup Jinja2 environment
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

def load_example_data(filename):
    """Load example data from the examples directory."""
    example_path = Path(__file__).parent.parent / "examples" / filename
    with open(example_path) as f:
        return json.load(f)

@pytest.mark.integration
def test_llm_sli_generation():
    """Test LLM generation of SLIs."""
    template = env.get_template("sli_generation.j2")
    input_data = load_example_data("sli_generation_input.json")
    
    # Generate prompt
    prompt = template.render(**input_data)
    
    # Call LLM
    response = call_llm(prompt)
    
    # Parse response as JSON
    output = json.loads(response)
    
    # Validate output schema
    assert validate_output(output)
    
    # Check key fields
    assert "slis" in output
    assert len(output["slis"]) > 0
    assert all("name" in sli for sli in output["slis"])
    assert all("type" in sli for sli in output["slis"])
    assert all("thresholds" in sli for sli in output["slis"])

@pytest.mark.integration
def test_llm_slo_generation():
    """Test LLM generation of SLOs."""
    template = env.get_template("slo_generation.j2")
    input_data = load_example_data("slo_generation_input.json")
    
    # Generate prompt
    prompt = template.render(**input_data)
    
    # Call LLM
    response = call_llm(prompt)
    
    # Parse response as JSON
    output = json.loads(response)
    
    # Validate output schema
    assert validate_output(output)
    
    # Check key fields
    assert "slos" in output
    assert len(output["slos"]) > 0
    assert all("name" in slo for slo in output["slos"])
    assert all("target" in slo for slo in output["slos"])
    assert all("error_budget" in slo for slo in output["slos"])

@pytest.mark.integration
def test_llm_alert_generation():
    """Test LLM generation of alerts."""
    template = env.get_template("alert_generation.j2")
    input_data = load_example_data("alert_generation_input.json")
    
    # Generate prompt
    prompt = template.render(**input_data)
    
    # Call LLM
    response = call_llm(prompt)
    
    # Parse response as JSON
    output = json.loads(response)
    
    # Validate output schema
    assert validate_output(output)
    
    # Check key fields
    assert "alerts" in output
    assert len(output["alerts"]) > 0
    assert all("name" in alert for alert in output["alerts"])
    assert all("severity" in alert for alert in output["alerts"])
    assert all("notifications" in alert for alert in output["alerts"])

@pytest.mark.integration
def test_llm_analysis():
    """Test LLM generation of service analysis."""
    template = env.get_template("analysis.j2")
    input_data = load_example_data("analysis_input.json")
    
    # Generate prompt
    prompt = template.render(**input_data)
    
    # Call LLM
    response = call_llm(prompt)
    
    # Parse response as JSON
    output = json.loads(response)
    
    # Validate output schema
    assert validate_output(output)
    
    # Check key fields
    assert "current_state" in output
    assert "recommendations" in output
    assert "risks" in output
    assert len(output["recommendations"]) > 0
    assert len(output["risks"]) > 0

@pytest.mark.integration
def test_llm_runbook():
    """Test LLM generation of runbooks."""
    template = env.get_template("runbook.j2")
    input_data = load_example_data("runbook_input.json")
    
    # Generate prompt
    prompt = template.render(**input_data)
    
    # Call LLM
    response = call_llm(prompt)
    
    # Parse response as JSON
    output = json.loads(response)
    
    # Validate output schema
    assert validate_output(output)
    
    # Check key fields
    assert "runbooks" in output
    assert len(output["runbooks"]) > 0
    assert all("investigation" in runbook for runbook in output["runbooks"])
    assert all("resolution" in runbook for runbook in output["runbooks"])
    assert all("escalation" in runbook for runbook in output["runbooks"])

@pytest.mark.integration
def test_llm_end_to_end():
    """Test end-to-end LLM generation for all templates."""
    # Load all example data
    sli_input = load_example_data("sli_generation_input.json")
    slo_input = load_example_data("slo_generation_input.json")
    alert_input = load_example_data("alert_generation_input.json")
    analysis_input = load_example_data("analysis_input.json")
    runbook_input = load_example_data("runbook_input.json")
    
    # Generate and validate SLIs
    sli_template = env.get_template("sli_generation.j2")
    sli_prompt = sli_template.render(**sli_input)
    sli_response = call_llm(sli_prompt)
    sli_output = json.loads(sli_response)
    assert validate_output(sli_output)
    
    # Generate and validate SLOs
    slo_template = env.get_template("slo_generation.j2")
    slo_prompt = slo_template.render(**slo_input)
    slo_response = call_llm(slo_prompt)
    slo_output = json.loads(slo_response)
    assert validate_output(slo_output)
    
    # Generate and validate alerts
    alert_template = env.get_template("alert_generation.j2")
    alert_prompt = alert_template.render(**alert_input)
    alert_response = call_llm(alert_prompt)
    alert_output = json.loads(alert_response)
    assert validate_output(alert_output)
    
    # Generate and validate analysis
    analysis_template = env.get_template("analysis.j2")
    analysis_prompt = analysis_template.render(**analysis_input)
    analysis_response = call_llm(analysis_prompt)
    analysis_output = json.loads(analysis_response)
    assert validate_output(analysis_output)
    
    # Generate and validate runbooks
    runbook_template = env.get_template("runbook.j2")
    runbook_prompt = runbook_template.render(**runbook_input)
    runbook_response = call_llm(runbook_prompt)
    runbook_output = json.loads(runbook_response)
    assert validate_output(runbook_output)
    
    # Verify consistency between outputs
    assert sli_output["metadata"]["service_name"] == slo_output["metadata"]["service_name"]
    assert slo_output["metadata"]["service_name"] == alert_output["metadata"]["service_name"]
    assert alert_output["metadata"]["service_name"] == analysis_output["metadata"]["service_name"]
    assert analysis_output["metadata"]["service_name"] == runbook_output["metadata"]["service_name"] 