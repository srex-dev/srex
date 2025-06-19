# api/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models_llm import engine, SessionLocal, Base, LLMOutput, DriftAnalysis
from .models_policy import Policy as PolicyModel, Base as PolicyBase
from core.middleware import setup_middleware
from core.config import settings
from .metrics import router as metrics_router
from .v1 import router as v1_router
from .drift import router as drift_router
from .scorecard import router as scorecard_router
from .llm import router as llm_router
import uuid
from datetime import datetime, timedelta

app = FastAPI(
    title="SREx API",
    description="API for generating and validating policies, SLOs, and more",
    version="0.1.0"
)

# Setup middleware
setup_middleware(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "SREx API is running"}

# Include routers
app.include_router(metrics_router, prefix="/api/metrics")
app.include_router(v1_router)
app.include_router(drift_router, prefix="/api")
app.include_router(scorecard_router, prefix="/api")
app.include_router(llm_router, prefix="/api/llm")

# Create tables at startup
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(PolicyBase.metadata.create_all)

# LLM endpoints
@app.post("/api/llm/generate")
async def generate_llm_response(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.json()
        # Import here to avoid circular import issues
        from backend.core.services.prompt.prompt_engine import generate_prompt_response
        response = await generate_prompt_response(body)
        
        # Save to database with confidence
        confidence = response.get("ai_confidence", 0.0)
        llm_output = LLMOutput(
            id=str(uuid.uuid4()),
            task="single_analysis",
            input=body,
            output=response,
            confidence=confidence,
            explanation=response.get("explanation", "")
        )
        
        db.add(llm_output)
        await db.commit()
        
        return response
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate response: {str(e)}"}
        )

@app.post("/api/llm/5step")
async def generate_5step_response(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.json()
        # Import here to avoid circular import issues
        from backend.core.services.prompt.prompt_engine import generate_prompt_response_5step
        response = await generate_prompt_response_5step(body)
        
        # Save to database with confidence
        confidence = response.get("ai_confidence", 0.0)
        llm_output = LLMOutput(
            id=str(uuid.uuid4()),
            task="5step_analysis",
            input=body,
            output=response,
            confidence=confidence,
            explanation=response.get("explanation", "")
        )
        
        db.add(llm_output)
        await db.commit()
        
        return response
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate 5-step response: {str(e)}"}
        )

@app.get("/api/llm/outputs")
async def get_llm_outputs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get LLM outputs with pagination"""
    query = select(LLMOutput).order_by(LLMOutput.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    outputs = result.scalars().all()
    
    return {
        "outputs": [
            {
                "id": output.id,
                "input": output.input,
                "output": output.output,
                "confidence": output.confidence,
                "created_at": output.created_at.isoformat(),
                "step_data": output.step_data,
                "metadata": output.metadata
            }
            for output in outputs
        ],
        "total": len(outputs),
        "skip": skip,
        "limit": limit
    }

@app.get("/api/llm/components")
async def get_components():
    """Get available components for analysis"""
    # This would typically come from a database or configuration
    # For now, returning a static list
    return [
        "user-service",
        "payment-service", 
        "notification-service",
        "auth-service",
        "api-gateway",
        "database-service",
        "cache-service",
        "search-service",
        "file-service",
        "analytics-service"
    ]

@app.get("/api/health")
async def api_health():
    """API health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/test/confidence")
async def test_confidence_storage(request: Request, db: AsyncSession = Depends(get_db)):
    """Test endpoint to create a mock LLM output with confidence for testing"""
    try:
        # Create a mock response with confidence
        mock_response = {
            "sli": [
                {
                    "name": "test_sli",
                    "type": "availability",
                    "description": "Test SLI for confidence validation"
                }
            ],
            "slo": [
                {
                    "name": "test_slo",
                    "target": 99.9,
                    "time_window": "30d"
                }
            ],
            "alerts": [
                {
                    "name": "test_alert",
                    "severity": "warning",
                    "expr": "up == 0"
                }
            ],
            "llm_suggestions": [
                {
                    "metric": "test",
                    "recommendation": "Test recommendation"
                }
            ],
            "explanation": "This is a test response for confidence validation",
            "ai_confidence": 92.5  # Mock confidence value
        }
        
        # Save to database with confidence
        llm_output = LLMOutput(
            id=str(uuid.uuid4()),
            task="test_confidence",
            input={"test": "confidence_validation"},
            output=mock_response,
            confidence=mock_response["ai_confidence"],
            explanation=mock_response["explanation"]
        )
        
        db.add(llm_output)
        await db.commit()
        
        return {
            "message": "Test confidence record created successfully",
            "confidence": mock_response["ai_confidence"],
            "id": llm_output.id
        }
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to create test confidence record: {str(e)}"}
        )
