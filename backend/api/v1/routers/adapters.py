from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from backend.core.domain.security.security import get_current_active_user
from backend.core.domain.security.api_keys import validate_api_key
from backend.core.domain.metrics.loader import load_metrics_adapter
from core.config import CONFIG

router = APIRouter(prefix="/adapters", tags=["adapters"])

@router.get("/components")
async def get_available_components() -> List[str]:
    """Get available components from the configured metrics adapter."""
    try:
        adapter = load_metrics_adapter(CONFIG.metrics)
        if not adapter:
            raise HTTPException(status_code=500, detail="No metrics adapter configured")
        
        components = adapter.get_available_components()
        return components
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get components: {str(e)}")

# Add adapter endpoints here 