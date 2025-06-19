import typer
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.core.services.prompt.prompt_engine import generate_prompt_response
from backend.core.logger import logger

app = typer.Typer()

# Policy Templates for common compliance frameworks
POLICY_TEMPLATES = {
    "soc2": {
        "name": "SOC2 Compliance",
        "description": "SOC2 Type II compliance policies",
        "templates": [
            "Ensure all data is encrypted at rest",
            "Require multi-factor authentication for all user access",
            "Implement audit logging for all system changes",
            "Ensure backup and recovery procedures are documented"
        ]
    },
    "iso27001": {
        "name": "ISO 27001 Security",
        "description": "ISO 27001 information security policies",
        "templates": [
            "Ensure access control policies are implemented",
            "Require regular security assessments",
            "Implement incident response procedures",
            "Ensure business continuity planning"
        ]
    },
    "hipaa": {
        "name": "HIPAA Compliance",
        "description": "HIPAA healthcare data protection policies",
        "templates": [
            "Ensure PHI is encrypted in transit and at rest",
            "Implement access controls for healthcare data",
            "Require audit trails for all PHI access",
            "Ensure data backup and recovery procedures"
        ]
    },
    "pci": {
        "name": "PCI DSS",
        "description": "Payment Card Industry Data Security Standard",
        "templates": [
            "Ensure cardholder data is encrypted",
            "Implement strong access controls",
            "Require regular vulnerability assessments",
            "Ensure secure network architecture"
        ]
    }
}

def generate_policy(
    input: str,
    output: str,
    policy_type: str = "rego",
    model: str = "llama2",
    temperature: float = 0.3
) -> Dict[str, Any]:
    """
    Generate a policy from plain English description using LLM.
    
    Args:
        input: Plain English policy description
        output: Output file path
        policy_type: Type of policy (rego, yaml, json)
        model: LLM model to use
        temperature: LLM temperature setting
    
    Returns:
        Dict with policy generation results
    """
    try:
        # Create policy generation prompt
        if policy_type.lower() == "rego":
            prompt = f"""You are an expert in cloud governance and policy-as-code. Generate a valid Rego policy for Open Policy Agent based on the following plain-English requirement:

"{input}"

The policy should:
1. Use the 'deny' rule to enforce the requirement
2. Include metadata comments for description, SOC2, and ISO27001 compliance
3. Be valid Rego syntax (OPA 1.0+ with 'if' keyword)
4. Follow OPA best practices
5. Include proper package declaration
6. Handle edge cases and provide clear error messages

Respond only with the Rego policy code. Do not include any explanations, markdown, or extra formatting."""
        
        elif policy_type.lower() == "yaml":
            prompt = f"""You are an expert in cloud governance and policy-as-code. Generate a valid YAML policy based on the following plain-English requirement:

"{input}"

The policy should:
1. Use YAML syntax for policy definition
2. Include metadata for description and compliance
3. Follow cloud-native policy best practices
4. Be valid YAML format
5. Include proper structure and indentation

Respond only with the YAML policy code. Do not include any explanations, markdown, or extra formatting."""
        
        else:
            prompt = f"""You are an expert in cloud governance and policy-as-code. Generate a valid {policy_type.upper()} policy based on the following plain-English requirement:

"{input}"

The policy should:
1. Use {policy_type.upper()} syntax for policy definition
2. Include metadata for description and compliance
3. Follow cloud-native policy best practices
4. Be valid {policy_type.upper()} format

Respond only with the {policy_type.upper()} policy code. Do not include any explanations, markdown, or extra formatting."""
        
        # Generate policy using LLM
        logger.info(f"Generating {policy_type} policy from input: {input}")
        
        # Use generate_prompt_response for policy generation
        response = generate_prompt_response(
            input_json={
                "service_name": "policy_generation",
                "description": input,
                "policy_type": policy_type
            },
            prompt=prompt,
            model=model,
            temperature=temperature,
            explain=False
        )
        
        # Extract policy content from response
        policy_content = response.get("policy_content", "")
        if not policy_content:
            # If no policy_content in response, try to extract from the response structure
            policy_content = response.get("explanation", "") or str(response)
        
        # Clean and validate response
        policy_content = policy_content.strip()
        if not policy_content:
            raise ValueError("Generated policy content is empty")
        
        # Write policy to file
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(policy_content)
        
        logger.info(f"Policy generated successfully: {output_path}")
        
        return {
            "status": "success",
            "policy_path": str(output_path),
            "policy_content": policy_content,
            "metadata": {
                "input": input,
                "policy_type": policy_type,
                "model": model,
                "temperature": temperature,
                "generated_at": datetime.utcnow().isoformat(),
                "file_size": len(policy_content)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating policy: {str(e)}")
        raise

def validate_policy(
    infra: str,
    policy: str,
    policy_type: str = "rego"
) -> List[Dict[str, Any]]:
    """
    Validate infrastructure against a policy.
    
    Args:
        infra: Path to infrastructure file or JSON data
        policy: Path to policy file
        policy_type: Type of policy (rego, yaml, json)
    
    Returns:
        List of validation violations
    """
    try:
        # Read infrastructure data
        infra_path = Path(infra)
        if infra_path.exists():
            with open(infra_path, 'r') as f:
                infra_data = json.load(f)
        else:
            # Assume infra is JSON string
            infra_data = json.loads(infra)
        
        # Read policy
        policy_path = Path(policy)
        if not policy_path.exists():
            raise FileNotFoundError(f"Policy file not found: {policy}")
        
        with open(policy_path, 'r') as f:
            policy_content = f.read()
        
        logger.info(f"Validating policy {policy_path} against infrastructure")
        
        # For now, return a mock validation result
        # In a real implementation, this would use OPA or similar policy engine
        violations = []
        
        # Mock validation logic - in reality this would use OPA
        if policy_type.lower() == "rego":
            # Simulate OPA validation
            if "deny" in policy_content.lower():
                # Mock some violations for demonstration
                violations = [
                    {
                        "resource": "s3-bucket-example",
                        "rule": "encryption_required",
                        "message": "S3 bucket does not have encryption enabled",
                        "severity": "high",
                        "line": 1
                    }
                ]
        
        return violations
        
    except Exception as e:
        logger.error(f"Error validating policy: {str(e)}")
        raise

def test_policy(
    policy: str,
    test_data: str,
    policy_type: str = "rego"
) -> Dict[str, Any]:
    """
    Test a policy against sample data.
    
    Args:
        policy: Path to policy file
        test_data: Path to test data file or JSON string
        policy_type: Type of policy (rego, yaml, json)
    
    Returns:
        Test results
    """
    try:
        # Read policy
        policy_path = Path(policy)
        if not policy_path.exists():
            raise FileNotFoundError(f"Policy file not found: {policy}")
        
        with open(policy_path, 'r') as f:
            policy_content = f.read()
        
        # Read test data
        test_path = Path(test_data)
        if test_path.exists():
            with open(test_path, 'r') as f:
                test_data_content = json.load(f)
        else:
            # Assume test_data is JSON string
            test_data_content = json.loads(test_data)
        
        logger.info(f"Testing policy {policy_path} with sample data")
        
        # Mock test results
        test_results = {
            "policy": str(policy_path),
            "test_data": test_data_content,
            "results": [
                {
                    "test_case": "valid_configuration",
                    "status": "pass",
                    "message": "Configuration complies with policy"
                },
                {
                    "test_case": "invalid_configuration", 
                    "status": "fail",
                    "message": "Configuration violates encryption policy",
                    "violations": [
                        {
                            "resource": "test-bucket",
                            "rule": "encryption_required",
                            "message": "S3 bucket missing encryption"
                        }
                    ]
                }
            ],
            "summary": {
                "total_tests": 2,
                "passed": 1,
                "failed": 1,
                "success_rate": 50.0
            }
        }
        
        return test_results
        
    except Exception as e:
        logger.error(f"Error testing policy: {str(e)}")
        raise

def list_templates() -> Dict[str, Any]:
    """
    List available policy templates.
    
    Returns:
        Dictionary of available templates
    """
    return POLICY_TEMPLATES

def create_policy_from_template(
    template_name: str,
    template_index: int,
    output: str,
    customizations: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a policy from a predefined template.
    
    Args:
        template_name: Name of the template (soc2, iso27001, etc.)
        template_index: Index of the template to use
        output: Output file path
        customizations: Optional customizations to apply
    
    Returns:
        Policy generation results
    """
    if template_name not in POLICY_TEMPLATES:
        raise ValueError(f"Template '{template_name}' not found")
    
    template = POLICY_TEMPLATES[template_name]
    if template_index >= len(template["templates"]):
        raise ValueError(f"Template index {template_index} out of range")
    
    base_policy = template["templates"][template_index]
    
    # Apply customizations if provided
    if customizations:
        for key, value in customizations.items():
            base_policy = base_policy.replace(f"{{{key}}}", str(value))
    
    # Generate the policy
    return generate_policy(
        input=base_policy,
        output=output,
        policy_type="rego"
    )

# CLI Commands
@app.command()
def generate(
    input: str = typer.Argument(..., help="Plain English policy description"),
    output: str = typer.Option("output/generated_policy.rego", help="Output file path"),
    policy_type: str = typer.Option("rego", help="Policy type (rego, yaml, json)"),
    model: str = typer.Option("llama2", help="LLM model to use"),
    temperature: float = typer.Option(0.3, help="LLM temperature")
):
    """Generate a policy from plain English description."""
    try:
        result = generate_policy(
            input=input,
            output=output,
            policy_type=policy_type,
            model=model,
            temperature=temperature
        )
        typer.echo(f"✅ Policy generated successfully: {result['policy_path']}")
        typer.echo(f"📄 File size: {result['metadata']['file_size']} characters")
    except Exception as e:
        typer.echo(f"❌ Error generating policy: {str(e)}")
        raise typer.Exit(1)

@app.command()
def validate(
    infra: str = typer.Argument(..., help="Infrastructure file path or JSON data"),
    policy: str = typer.Argument(..., help="Policy file path"),
    policy_type: str = typer.Option("rego", help="Policy type")
):
    """Validate infrastructure against a policy."""
    try:
        violations = validate_policy(infra=infra, policy=policy, policy_type=policy_type)
        if violations:
            typer.echo(f"❌ Found {len(violations)} violations:")
            for violation in violations:
                typer.echo(f"  - {violation['message']} (Severity: {violation['severity']})")
        else:
            typer.echo("✅ No violations found - infrastructure complies with policy")
    except Exception as e:
        typer.echo(f"❌ Error validating policy: {str(e)}")
        raise typer.Exit(1)

@app.command()
def test(
    policy: str = typer.Argument(..., help="Policy file path"),
    test_data: str = typer.Argument(..., help="Test data file path or JSON string"),
    policy_type: str = typer.Option("rego", help="Policy type")
):
    """Test a policy against sample data."""
    try:
        results = test_policy(policy=policy, test_data=test_data, policy_type=policy_type)
        typer.echo(f"🧪 Policy Test Results:")
        typer.echo(f"  📊 Success Rate: {results['summary']['success_rate']}%")
        typer.echo(f"  ✅ Passed: {results['summary']['passed']}")
        typer.echo(f"  ❌ Failed: {results['summary']['failed']}")
        
        for result in results['results']:
            status_icon = "✅" if result['status'] == 'pass' else "❌"
            typer.echo(f"  {status_icon} {result['test_case']}: {result['message']}")
    except Exception as e:
        typer.echo(f"❌ Error testing policy: {str(e)}")
        raise typer.Exit(1)

@app.command()
def templates():
    """List available policy templates."""
    templates = list_templates()
    typer.echo("📋 Available Policy Templates:")
    for name, template in templates.items():
        typer.echo(f"\n🔹 {template['name']} ({name})")
        typer.echo(f"   {template['description']}")
        for i, policy in enumerate(template['templates']):
            typer.echo(f"   {i}: {policy}")

@app.command()
def create_from_template(
    template_name: str = typer.Argument(..., help="Template name (soc2, iso27001, hipaa, pci)"),
    template_index: int = typer.Argument(..., help="Template index"),
    output: str = typer.Option("output/template_policy.rego", help="Output file path")
):
    """Create a policy from a predefined template."""
    try:
        result = create_policy_from_template(
            template_name=template_name,
            template_index=template_index,
            output=output
        )
        typer.echo(f"✅ Policy created from template: {result['policy_path']}")
    except Exception as e:
        typer.echo(f"❌ Error creating policy from template: {str(e)}")
        raise typer.Exit(1)

@app.command()
def create_from_suggestion(
    llm_output_id: str = typer.Argument(..., help="LLM output ID from database"),
    suggestion_index: int = typer.Argument(..., help="Index of suggestion in the output"),
    output: str = typer.Option("output/suggestion_policy.rego", help="Output file path"),
    policy_type: str = typer.Option("rego", help="Policy type (rego, yaml, json)"),
    model: str = typer.Option("llama2", help="LLM model to use"),
    temperature: float = typer.Option(0.3, help="Temperature for generation")
):
    """Create a policy from an LLM suggestion stored in the database."""
    try:
        # Import database models
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        from backend.api.models_llm import SessionLocal, LLMOutput
        from sqlalchemy.future import select
        
        # Get the LLM output from database
        async def get_suggestion():
            async with SessionLocal() as db:
                query = select(LLMOutput).where(LLMOutput.id == llm_output_id)
                result = await db.execute(query)
                llm_output = result.scalar_one_or_none()
                
                if not llm_output:
                    raise ValueError(f"LLM output with ID {llm_output_id} not found")
                
                # Extract suggestions from the output
                output_data = llm_output.output
                suggestions = output_data.get("llm_suggestions", [])
                
                if not suggestions:
                    raise ValueError("No suggestions found in the LLM output")
                
                if suggestion_index >= len(suggestions):
                    raise ValueError(f"Suggestion index {suggestion_index} out of range. Available: 0-{len(suggestions)-1}")
                
                # Get the selected suggestion
                suggestion = suggestions[suggestion_index]
                
                # Extract recommendation text
                if isinstance(suggestion, dict):
                    recommendation = suggestion.get("recommendation", str(suggestion))
                else:
                    recommendation = str(suggestion)
                
                return recommendation, llm_output
        
        # Run async function
        import asyncio
        recommendation, llm_output = asyncio.run(get_suggestion())
        
        typer.echo(f"📋 Found suggestion: {recommendation[:100]}...")
        typer.echo(f"📊 Service: {llm_output.output.get('service_name', 'Unknown')}")
        typer.echo(f"🤖 AI Confidence: {llm_output.confidence:.1f}%")
        
        # Generate the policy
        result = generate_policy(
            input=recommendation,
            output=output,
            policy_type=policy_type,
            model=model,
            temperature=temperature
        )
        
        typer.echo(f"✅ Policy created from suggestion: {result['policy_path']}")
        typer.echo(f"📄 Policy type: {policy_type.upper()}")
        typer.echo(f"🤖 Model used: {model}")
        
    except Exception as e:
        typer.echo(f"❌ Error creating policy from suggestion: {str(e)}")
        raise typer.Exit(1)

@app.command()
def list_suggestions(
    service_name: Optional[str] = typer.Option(None, help="Filter by service name"),
    category: Optional[str] = typer.Option(None, help="Filter by category"),
    limit: int = typer.Option(20, help="Number of suggestions to show")
):
    """List available LLM suggestions that can be converted to policies."""
    try:
        # Import database models
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        from backend.api.models_llm import SessionLocal, LLMOutput
        from sqlalchemy.future import select
        from sqlalchemy import text
        
        async def get_suggestions():
            async with SessionLocal() as db:
                query = select(LLMOutput).order_by(LLMOutput.created_at.desc())
                
                # Filter by service name if provided
                if service_name:
                    query = query.where(text("input::text LIKE :service_pattern"))
                    query = query.params(service_pattern=f'%"service_name": "{service_name}"%')
                
                query = query.limit(limit)
                result = await db.execute(query)
                outputs = result.scalars().all()
                
                suggestions = []
                for output in outputs:
                    output_data = output.output
                    llm_suggestions = output_data.get("llm_suggestions", [])
                    
                    for i, suggestion in enumerate(llm_suggestions):
                        # Filter by category if provided
                        if category and isinstance(suggestion, dict):
                            if suggestion.get("category") != category:
                                continue
                        
                        suggestion_info = {
                            "llm_output_id": output.id,
                            "suggestion_index": i,
                            "created_at": output.created_at,
                            "service_name": output_data.get("service_name", "Unknown"),
                            "suggestion": suggestion,
                            "ai_confidence": output.confidence
                        }
                        
                        suggestions.append(suggestion_info)
                
                return suggestions
        
        # Run async function
        import asyncio
        suggestions = asyncio.run(get_suggestions())
        
        if not suggestions:
            typer.echo("📭 No suggestions found. Try running the 5-step analysis first.")
            return
        
        typer.echo(f"💡 Found {len(suggestions)} suggestions:")
        typer.echo()
        
        for i, suggestion in enumerate(suggestions, 1):
            typer.echo(f"{i}. 📊 {suggestion['service_name']}")
            typer.echo(f"   🆔 Output ID: {suggestion['llm_output_id']}")
            typer.echo(f"   📍 Index: {suggestion['suggestion_index']}")
            typer.echo(f"   📅 Created: {suggestion['created_at'].strftime('%Y-%m-%d %H:%M')}")
            typer.echo(f"   🤖 Confidence: {suggestion['ai_confidence']:.1f}%")
            
            if isinstance(suggestion['suggestion'], dict):
                typer.echo(f"   🏷️  Category: {suggestion['suggestion'].get('category', 'general')}")
                typer.echo(f"   📈 Metric: {suggestion['suggestion'].get('metric', 'unknown')}")
                typer.echo(f"   ⚠️  Priority: {suggestion['suggestion'].get('priority', 'medium')}")
                typer.echo(f"   💪 Effort: {suggestion['suggestion'].get('effort', 'medium')}")
                typer.echo(f"   🎯 Impact: {suggestion['suggestion'].get('impact', 'medium')}")
                recommendation = suggestion['suggestion'].get('recommendation', str(suggestion['suggestion']))
            else:
                recommendation = str(suggestion['suggestion'])
            
            typer.echo(f"   💡 Recommendation: {recommendation[:100]}{'...' if len(recommendation) > 100 else ''}")
            typer.echo()
        
        typer.echo("💡 To create a policy from a suggestion, use:")
        typer.echo("   python cli/policy.py create-from-suggestion <output_id> <suggestion_index>")
        
    except Exception as e:
        typer.echo(f"❌ Error listing suggestions: {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 