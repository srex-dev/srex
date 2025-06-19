from pydantic import BaseModel
from typing import Optional, List

class APIKeyCreate(BaseModel):
    name: str
    scopes: Optional[List[str]] = []

class APIKeyResponse(BaseModel):
    api_key: str
    name: Optional[str] = None
    scopes: Optional[List[str]] = []

def create_api_key(*args, **kwargs):
    return {"api_key": "stub_api_key"}

def revoke_api_key(*args, **kwargs):
    return {"revoked": True}

def list_api_keys(*args, **kwargs):
    return ["stub_api_key_1", "stub_api_key_2"]

def validate_api_key(*args, **kwargs):
    return "stub_api_key"

def check_api_key_scopes(*args, **kwargs):
    return True 