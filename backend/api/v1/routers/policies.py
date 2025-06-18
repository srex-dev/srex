from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
from pathlib import Path

from core.domain.security.security import User, get_current_active_user, check_permissions
from core.domain.security.api_keys import validate_api_key, check_api_key_scopes
from core.services.logging.logger import logger
from cli.policy import generate_policy, validate_policy

router = APIRouter(prefix="/policies", tags=["policies"])

# Policy Models
class PolicyGenerationRequest(BaseModel):
    input: str
    policy_type: str = "rego"
    model: str = "llama2"
    temperature: float = 0.3
    max_retries: int = 2

class PolicyValidationRequest(BaseModel):
    policy_path: str
    infra_path: str

class PolicyResponse(BaseModel):
    status: str
    message: Optional[str] = None
    policy_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ValidationResponse(BaseModel):
    status: str
    message: Optional[str] = None
    violations: Optional[List[Dict[str, Any]]] = None

@router.post("/generate", response_model=PolicyResponse)
async def generate_policy_endpoint(
    request: PolicyGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    api_key: Optional[str] = Depends(validate_api_key)
):
    """
    Generate a policy from a plain English description.
    """
    # Check permissions from either JWT or API key
    if current_user and not check_permissions(current_user, ["write"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    if api_key and not check_api_key_scopes(["write"])(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not have required permissions"
        )
    
    try:
        # Generate a unique filename
        timestamp = int(time.time())
        output_path = Path("output") / f"generated_{request.policy_type}_{timestamp}.{request.policy_type}"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating policy from input: {request.input}")
        generate_policy(
            input=request.input,
            output=str(output_path),
            policy_type=request.policy_type,
            model=request.model,
            temperature=request.temperature,
            max_retries=request.max_retries
        )
        
        return PolicyResponse(
            status="success",
            policy_path=str(output_path),
            metadata={
                "type": request.policy_type,
                "model": request.model,
                "temperature": request.temperature
            }
        )
    except Exception as e:
        logger.error(f"Error generating policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate policy: {str(e)}"
        )

@router.post("/validate", response_model=ValidationResponse)
async def validate_policy_endpoint(request: PolicyValidationRequest):
    """
    Validate infrastructure against a policy.
    """
    try:
        # Verify files exist
        policy_path = Path(request.policy_path)
        infra_path = Path(request.infra_path)
        
        if not policy_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy file not found: {request.policy_path}"
            )
        if not infra_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Infrastructure file not found: {request.infra_path}"
            )
        
        logger.info(f"Validating policy {policy_path} against infrastructure {infra_path}")
        violations = validate_policy(
            infra=str(infra_path),
            policy=str(policy_path)
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