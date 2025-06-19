from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
from pathlib import Path

from backend.core.domain.security.security import User, get_current_active_user, check_permissions
from backend.core.domain.security.api_keys import validate_api_key, check_api_key_scopes
from backend.core.logger import logger
from backend.core.domain.slo.slo import get_slo_history, analyze_slo_trend

router = APIRouter(prefix="/slos", tags=["slos"])

# SLO Models
class SLOGenerationRequest(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = None
    model: str = "llama2"
    temperature: float = 0.3
    explain: bool = False

class SLOValidationRequest(BaseModel):
    slo_path: str
    metrics_path: Optional[str] = None
    live_metrics: bool = False
    adapter: Optional[str] = None

class SLOResponse(BaseModel):
    status: str
    message: Optional[str] = None
    slo_path: Optional[str] = None
    explanation: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SLODriftRequest(BaseModel):
    slo_path: str
    baseline_path: Optional[str] = None
    time_range: Optional[Dict[str, str]] = None
    adapter: Optional[str] = None
    threshold: float = 0.1  # 10% drift threshold

class SLODriftResponse(BaseModel):
    status: str
    message: Optional[str] = None
    drift_percentage: Optional[float] = None
    trend: Optional[str] = None  # "improving", "degrading", "stable"
    recommendations: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class SLOHistoryRequest(BaseModel):
    slo_path: str
    time_range: Optional[Dict[str, str]] = None
    interval: str = "1h"
    adapter: Optional[str] = None
    include_metadata: bool = True

class SLOHistoryResponse(BaseModel):
    status: str
    message: Optional[str] = None
    history: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

class SLOTrendRequest(BaseModel):
    slo_path: str
    time_range: Optional[Dict[str, str]] = None
    trend_type: str = "linear"
    window: str = "7d"
    adapter: Optional[str] = None

class SLOTrendResponse(BaseModel):
    status: str
    message: Optional[str] = None
    trend: Dict[str, Any]
    forecast: List[Dict[str, Any]]
    metadata: Dict[str, Any]

@router.post("/generate", response_model=SLOResponse)
async def generate_slo_endpoint(request: SLOGenerationRequest):
    """
    Generate an SLO from a plain English description.
    """
    try:
        timestamp = int(time.time())
        output_path = Path("output") / f"generated_slo_{timestamp}.yaml"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating SLO from input: {request.input}")
        # TODO: Implement SLO generation logic
        return {
            "status": "success",
            "slo_path": str(output_path),
            "explanation": "SLO generation logic not implemented",
            "metadata": {
                "model": request.model,
                "temperature": request.temperature,
                "explain": request.explain
            }
        }
    except Exception as e:
        logger.error(f"Error generating SLO: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SLO: {str(e)}"
        )

@router.post("/validate", response_model=SLOResponse)
async def validate_slo_endpoint(request: SLOValidationRequest):
    """
    Validate an SLO against metrics.
    """
    try:
        slo_path = Path(request.slo_path)
        if not slo_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SLO file not found: {request.slo_path}"
            )
        
        if request.live_metrics and not request.adapter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Adapter must be specified when using live metrics"
            )
        
        logger.info(f"Validating SLO {slo_path}")
        # TODO: Implement SLO validation logic
        return {
            "status": "success",
            "message": "SLO validation logic not implemented"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating SLO: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate SLO: {str(e)}"
        )

@router.post("/drift", response_model=SLODriftResponse)
async def analyze_slo_drift(request: SLODriftRequest):
    """Analyze SLO drift over time."""
    try:
        slo_path = Path(request.slo_path)
        if not slo_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SLO file not found: {request.slo_path}"
            )
        
        if request.live_metrics and not request.adapter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Adapter must be specified when using live metrics"
            )
        
        logger.info(f"Analyzing SLO drift for {slo_path}")
        # TODO: Implement SLO drift analysis logic
        return {
            "status": "success",
            "drift_percentage": 0.0,
            "trend": "stable",
            "recommendations": [],
            "metadata": {
                "threshold": request.threshold,
                "time_range": request.time_range
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing SLO drift: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze SLO drift: {str(e)}"
        )

@router.post("/history", response_model=SLOHistoryResponse)
async def get_slo_history_endpoint(request: SLOHistoryRequest):
    """Get historical data for an SLO."""
    try:
        # Accept both dict and string for time_range
        time_range = request.time_range
        if isinstance(time_range, dict):
            # Convert dict to string, e.g., {"value": 7, "unit": "d"} -> "7d"
            value = time_range.get("value")
            unit = time_range.get("unit")
            if value and unit:
                time_range = f"{value}{unit}"
            else:
                time_range = "7d"
        elif time_range is None:
            time_range = "7d"
            
        result = get_slo_history(
            slo_path=request.slo_path,
            time_range=time_range,
            interval=request.interval,
            adapter=request.adapter,
            include_metadata=request.include_metadata
        )
        return {
            "status": "success",
            "history": result["history"],
            "metadata": result.get("metadata")
        }
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SLO file not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting SLO history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get SLO history: {str(e)}"
        )

@router.post("/trend", response_model=SLOTrendResponse)
async def analyze_slo_trend_endpoint(request: SLOTrendRequest):
    """Analyze trends in SLO performance."""
    try:
        # Accept both dict and string for time_range
        time_range = request.time_range
        if isinstance(time_range, dict):
            value = time_range.get("value")
            unit = time_range.get("unit")
            if value and unit:
                time_range = f"{value}{unit}"
            else:
                time_range = "30d"
        elif time_range is None:
            time_range = "30d"
            
        result = analyze_slo_trend(
            slo_path=request.slo_path,
            time_range=time_range,
            trend_type=request.trend_type,
            window=request.window,
            adapter=request.adapter
        )
        return {
            "status": "success",
            "trend": result["trend"],
            "forecast": result.get("forecast"),
            "metadata": result["metadata"]
        }
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SLO file not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing SLO trend: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze SLO trend: {str(e)}"
        ) 