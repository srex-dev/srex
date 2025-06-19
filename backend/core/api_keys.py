import secrets
import string
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import os
from backend.core.logger import logger

# API Key configuration
API_KEY_HEADER = "X-API-Key"
API_KEY_PREFIX = "srex_"  # Prefix for API keys
API_KEY_LENGTH = 32  # Length of the random part
API_KEY_EXPIRY_DAYS = 90  # Days until API key expires

# API Key security
api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=True)

class APIKey(BaseModel):
    """API Key model."""
    key: str
    name: str
    created_at: datetime
    expires_at: datetime
    scopes: list[str]
    is_active: bool = True
    last_used: Optional[datetime] = None
    created_by: str

class APIKeyCreate(BaseModel):
    """API Key creation model."""
    name: str
    scopes: list[str]
    expires_in_days: Optional[int] = API_KEY_EXPIRY_DAYS

class APIKeyResponse(BaseModel):
    """API Key response model."""
    key: str
    name: str
    created_at: datetime
    expires_at: datetime
    scopes: list[str]

# In-memory storage - Replace with database in production
api_keys_db: Dict[str, APIKey] = {}

def generate_api_key() -> str:
    """Generate a secure API key."""
    # Generate random string
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(API_KEY_LENGTH))
    
    # Combine with prefix
    api_key = f"{API_KEY_PREFIX}{random_part}"
    
    # Hash the key for storage
    return api_key

def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()

def create_api_key(name: str, scopes: list[str], created_by: str, expires_in_days: int = API_KEY_EXPIRY_DAYS) -> APIKeyResponse:
    """Create a new API key."""
    # Generate API key
    api_key = generate_api_key()
    hashed_key = hash_api_key(api_key)
    
    # Create API key object
    now = datetime.utcnow()
    api_key_obj = APIKey(
        key=hashed_key,
        name=name,
        created_at=now,
        expires_at=now + timedelta(days=expires_in_days),
        scopes=scopes,
        created_by=created_by
    )
    
    # Store in database
    api_keys_db[hashed_key] = api_key_obj
    
    # Return response with unhashed key
    return APIKeyResponse(
        key=api_key,
        name=name,
        created_at=now,
        expires_at=now + timedelta(days=expires_in_days),
        scopes=scopes
    )

def validate_api_key(api_key: str = Security(api_key_header)) -> APIKey:
    """Validate an API key."""
    # Hash the provided key
    hashed_key = hash_api_key(api_key)
    
    # Check if key exists
    if hashed_key not in api_keys_db:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    # Get key object
    key_obj = api_keys_db[hashed_key]
    
    # Check if key is active
    if not key_obj.is_active:
        raise HTTPException(
            status_code=401,
            detail="API key is inactive"
        )
    
    # Check if key has expired
    if datetime.utcnow() > key_obj.expires_at:
        raise HTTPException(
            status_code=401,
            detail="API key has expired"
        )
    
    # Update last used timestamp
    key_obj.last_used = datetime.utcnow()
    
    return key_obj

def revoke_api_key(api_key: str) -> bool:
    """Revoke an API key."""
    hashed_key = hash_api_key(api_key)
    if hashed_key in api_keys_db:
        api_keys_db[hashed_key].is_active = False
        return True
    return False

def list_api_keys(created_by: Optional[str] = None) -> list[APIKey]:
    """List all API keys."""
    if created_by:
        return [key for key in api_keys_db.values() if key.created_by == created_by]
    return list(api_keys_db.values())

def check_api_key_scopes(required_scopes: list[str]):
    """Check if the API key has the required scopes."""
    async def scope_checker(api_key: APIKey = Depends(validate_api_key)):
        for scope in required_scopes:
            if scope not in api_key.scopes:
                raise HTTPException(
                    status_code=403,
                    detail=f"API key does not have required scope: {scope}"
                )
        return api_key
    return scope_checker 