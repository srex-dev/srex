from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, List, Dict, Any

from core.domain.security.security import (
    Token, User, authenticate_user, create_access_token,
    get_current_user, get_current_active_user
)
from core.domain.security.api_keys import (
    APIKeyCreate, APIKeyResponse, create_api_key, revoke_api_key,
    list_api_keys, validate_api_key
)

from backend.api.v1.routers.policies import router as policies_router
from backend.api.v1.routers.slos import router as slos_router
from backend.api.v1.routers.users import router as users_router
from backend.api.v1.routers.api_keys import router as api_keys_router
from backend.api.v1.routers.adapters import router as adapters_router
from backend.api.v1.routers.auth import router as auth_router

api_v1_router = APIRouter()
api_v1_router.include_router(policies_router)
api_v1_router.include_router(slos_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(api_keys_router)
api_v1_router.include_router(adapters_router)
api_v1_router.include_router(auth_router)

router = APIRouter(prefix="/api/v1")
router.include_router(api_v1_router)

# Authentication endpoint
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# API Key endpoints
@router.post("/api-keys", response_model=APIKeyResponse)
async def create_new_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user)
):
    return await create_api_key(api_key_data, current_user)

@router.get("/api-keys", response_model=List[APIKeyResponse])
async def get_api_keys(
    current_user: User = Depends(get_current_active_user)
):
    return await list_api_keys(current_user)

@router.delete("/api-keys/{api_key}")
async def delete_api_key(
    api_key: str,
    current_user: User = Depends(get_current_active_user)
):
    return await revoke_api_key(api_key, current_user)

# Health check endpoint
@router.get("/health")
async def health_check():
    return {"status": "healthy"}
