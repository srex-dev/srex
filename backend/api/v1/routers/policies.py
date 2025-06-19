from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
from pathlib import Path
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.core.domain.security.security import User, get_current_active_user, check_permissions
from backend.core.domain.security.api_keys import validate_api_key, check_api_key_scopes
from backend.core.logger import logger
from backend.core.services.policy.policy_generator import PolicyGenerator
from backend.core.services.policy.policy_suggestions import PolicySuggestionsService
from backend.api.models_llm import LLMOutput, SessionLocal
from sqlalchemy.future import select
from cli.policy import validate_policy, test_policy, list_templates, create_policy_from_template

router = APIRouter(prefix="/policies", tags=["policies"])

# Policy Models
class PolicyGenerationRequest(BaseModel):
    input: str
    policy_type: str = "rego"
    model: str = "llama2"
    temperature: float = 0.3
    name: Optional[str] = None
    additional_context: Optional[str] = None
    examples: Optional[str] = None

class PolicyValidationRequest(BaseModel):
    infra: str  # JSON string of infrastructure data
    policy: str  # Policy file path
    policy_type: str = "rego"

class PolicyResponse(BaseModel):
    status: str
    message: Optional[str] = None
    policy_path: Optional[str] = None
    policy_content: Optional[str] = None
    name: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class ValidationResponse(BaseModel):
    status: str
    message: Optional[str] = None
    violations: Optional[List[Dict[str, Any]]] = None

class PolicyTestRequest(BaseModel):
    policy: str
    test_data: str
    policy_type: str = "rego"

class PolicyTemplateRequest(BaseModel):
    template_name: str
    template_index: int
    output: str

class PolicyTemplateResponse(BaseModel):
    status: str
    policy_path: Optional[str] = None
    policy_content: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class PolicyFromSuggestionRequest(BaseModel):
    llm_output_id: str
    suggestion_index: int
    policy_type: str = "rego"
    model: str = "llama2"
    temperature: float = 0.3
    customizations: Optional[Dict[str, Any]] = None

class SuggestionsGenerationRequest(BaseModel):
    service_name: Optional[str] = None
    category: Optional[str] = None
    model: str = "llama2"
    temperature: float = 0.3

@router.post("/generate", response_model=PolicyResponse)
async def generate_policy_endpoint(request: PolicyGenerationRequest):
    """
    Generate a policy from a plain English description.
    """
    try:
        generator = PolicyGenerator(
            model=request.model,
            temperature=request.temperature
        )
        
        result = await generator.generate_policy(
            description=request.input,
            policy_type=request.policy_type,
            name=request.name,
            additional_context=request.additional_context,
            examples=request.examples,
            save_to_db=True
        )
        
        return PolicyResponse(
            status="success",
            policy_path=result["policy_path"],
            policy_content=result["policy_content"],
            name=result["name"],
            meta=result["meta"]
        )
    except Exception as e:
        logger.error(f"Error generating policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate policy: {str(e)}"
        )

@router.get("/templates")
async def get_policy_templates():
    """
    Get available policy templates.
    """
    try:
        templates = list_templates()
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch templates: {str(e)}"
        )

@router.get("/suggestions")
async def get_policy_suggestions(
    service_name: Optional[str] = None,
    category: Optional[str] = None
):
    """
    Get policy suggestions from LLM outputs.
    """
    try:
        service = PolicySuggestionsService()
        suggestions = await service.get_suggestions(
            service_name=service_name,
            category=category
        )
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Error fetching suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch suggestions: {str(e)}"
        )

@router.post("/generate-suggestions")
async def generate_policy_suggestions(request: SuggestionsGenerationRequest):
    """
    Generate new policy suggestions.
    """
    try:
        service = PolicySuggestionsService(
            model=request.model,
            temperature=request.temperature
        )
        result = await service.generate_suggestions(
            service_name=request.service_name,
            category=request.category,
            save_to_db=True
        )
        return result
    except Exception as e:
        logger.error(f"Error generating policy suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate policy suggestions: {str(e)}"
        )

@router.get("/list")
async def list_policies_endpoint(
    skip: int = 0,
    limit: int = 50,
    policy_type: Optional[str] = None,
    active_only: bool = True
):
    """
    List generated policies with pagination and filtering.
    """
    try:
        generator = PolicyGenerator()
        result = await generator.list_policies(
            skip=skip,
            limit=limit,
            policy_type=policy_type,
            active_only=active_only
        )
        return result
    except Exception as e:
        logger.error(f"Error listing policies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list policies: {str(e)}"
        )

@router.get("/{policy_id}")
async def get_policy_endpoint(policy_id: str):
    """
    Get a specific policy by ID.
    """
    try:
        generator = PolicyGenerator()
        policy = await generator.get_policy(policy_id)
        
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy with ID {policy_id} not found"
            )
        
        return policy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get policy: {str(e)}"
        )

@router.delete("/{policy_id}")
async def delete_policy_endpoint(policy_id: str):
    """
    Delete a policy (soft delete).
    """
    try:
        generator = PolicyGenerator()
        success = await generator.delete_policy(policy_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy with ID {policy_id} not found"
            )
        
        return {"status": "success", "message": f"Policy {policy_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete policy: {str(e)}"
        )

@router.post("/validate", response_model=ValidationResponse)
async def validate_policy_endpoint(request: PolicyValidationRequest):
    """
    Validate infrastructure against a policy.
    """
    try:
        # Verify policy file exists
        policy_path = Path(request.policy)
        
        if not policy_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy file not found: {request.policy}"
            )
        
        logger.info(f"Validating policy {policy_path} against infrastructure data")
        violations = validate_policy(
            infra=request.infra,  # JSON string from frontend
            policy=str(policy_path),
            policy_type=request.policy_type
        )
        
        return ValidationResponse(
            status="success",
            violations=violations
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate policy: {str(e)}"
        )

@router.post("/test")
async def test_policy_endpoint(request: PolicyTestRequest):
    """
    Test a policy against sample data.
    """
    try:
        results = test_policy(
            policy=request.policy,
            test_data=request.test_data,
            policy_type=request.policy_type
        )
        return results
    except Exception as e:
        logger.error(f"Error testing policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test policy: {str(e)}"
        )

@router.post("/create-from-template", response_model=PolicyTemplateResponse)
async def create_from_template_endpoint(request: PolicyTemplateRequest):
    """
    Create a policy from a predefined template.
    """
    try:
        result = create_policy_from_template(
            template_name=request.template_name,
            template_index=request.template_index,
            output=request.output
        )
        return PolicyTemplateResponse(
            status="success",
            policy_path=result.get("policy_path"),
            policy_content=result.get("policy_content"),
            meta=result.get("metadata")
        )
    except Exception as e:
        logger.error(f"Error creating policy from template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create policy from template: {str(e)}"
        )

@router.post("/create-from-suggestion", response_model=PolicyTemplateResponse)
async def create_policy_from_suggestion(request: PolicyFromSuggestionRequest):
    """
    Create a policy from an LLM suggestion stored in the database.
    """
    try:
        # Get the LLM output from database
        async with SessionLocal() as db:
            query = select(LLMOutput).where(LLMOutput.id == request.llm_output_id)
            result = await db.execute(query)
            llm_output = result.scalar_one_or_none()
            
            if not llm_output:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"LLM output with ID {request.llm_output_id} not found"
                )
            
            # Extract suggestions from the output
            output_data = llm_output.output
            suggestions = output_data.get("llm_suggestions", [])
            
            if not suggestions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No suggestions found in the LLM output"
                )
            
            if request.suggestion_index >= len(suggestions):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Suggestion index {request.suggestion_index} out of range. Available: 0-{len(suggestions)-1}"
                )
            
            # Get the selected suggestion
            suggestion = suggestions[request.suggestion_index]
            
            # Extract recommendation text
            if isinstance(suggestion, dict):
                recommendation = suggestion.get("recommendation", str(suggestion))
            else:
                recommendation = str(suggestion)
            
            # Apply customizations if provided
            if request.customizations:
                for key, value in request.customizations.items():
                    recommendation = recommendation.replace(f"{{{key}}}", str(value))
            
            # Generate filename based on suggestion
            suggestion_type = "suggestion"
            if isinstance(suggestion, dict):
                suggestion_type = suggestion.get("category", "suggestion")
                metric = suggestion.get("metric", "unknown")
            else:
                metric = "unknown"
            
            output_path = f"output/{suggestion_type}_{metric}_{request.llm_output_id}_{request.suggestion_index}.{request.policy_type}"
            
            # Generate the policy
            result = generate_policy(
                input=recommendation,
                output=output_path,
                policy_type=request.policy_type,
                model=request.model,
                temperature=request.temperature
            )
            
            return PolicyTemplateResponse(
                status="success",
                policy_path=result.get("policy_path"),
                policy_content=result.get("policy_content"),
                meta={
                    "llm_output_id": request.llm_output_id,
                    "suggestion_index": request.suggestion_index,
                    "suggestion": suggestion,
                    "original_recommendation": recommendation
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating policy from suggestion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create policy from suggestion: {str(e)}"
        ) 