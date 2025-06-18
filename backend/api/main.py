# api/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.api.models_llm import engine, SessionLocal, Base, LLMOutput
from core.middleware import setup_middleware
from core.config import settings
from .metrics import router as metrics_router
from .v1 import router as v1_router
from core.services.prompt.prompt_engine import generate_prompt_response, generate_prompt_response_5step
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

# Include routers
app.include_router(metrics_router, prefix="/api/metrics")
app.include_router(v1_router)

# Create tables at startup
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

def parse_timeframe(timeframe: str) -> timedelta:
    mapping = {
        "3m": timedelta(minutes=3),
        "5min": timedelta(minutes=5),
        "30min": timedelta(minutes=30),
        "1hr": timedelta(hours=1),
        "1d": timedelta(days=1),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
    }
    return mapping.get(timeframe, timedelta(minutes=5))

# Advanced LLM endpoint (original method)
@app.post("/llm")
async def llm_endpoint(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    template = data.get("task")
    input_data = data.get("input")
    provider = data.get("provider", "ollama")
    timeframe = input_data.get("timeframe", "5min")
    since = datetime.utcnow() - parse_timeframe(timeframe)
    result = generate_prompt_response(
        {**input_data, "since": since.isoformat(), "timeframe": timeframe}, 
        template=template,
        provider=provider
    )
    db_obj = LLMOutput(
        id=str(uuid.uuid4()),
        task=template,
        input=input_data,
        output=result,
        confidence=result.get("ai_confidence"),
        explanation=result.get("explanation"),
    )
    db.add(db_obj)
    await db.commit()
    return JSONResponse(content={"output": result})

# New 5-step LLM endpoint
@app.post("/llm/5step")
async def llm_5step_endpoint(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    input_data = data.get("input", {})
    model = data.get("model", "llama2")
    temperature = data.get("temperature", 0.7)
    provider = data.get("provider", "ollama")
    timeframe = input_data.get("timeframe", "5min")
    since = datetime.utcnow() - parse_timeframe(timeframe)
    
    result = generate_prompt_response_5step(
        {**input_data, "since": since.isoformat(), "timeframe": timeframe},
        model=model,
        temperature=temperature,
        provider=provider
    )
    
    db_obj = LLMOutput(
        id=str(uuid.uuid4()),
        task="5step_llm_process",
        input=input_data,
        output=result,
        confidence=result.get("ai_confidence"),
        explanation=result.get("explanation"),
    )
    db.add(db_obj)
    await db.commit()
    return JSONResponse(content={"output": result})

# LLM Output History endpoint
@app.get("/llm/history")
async def llm_history(db: AsyncSession = Depends(get_db), limit: int = 20):
    result = await db.execute(select(LLMOutput).order_by(LLMOutput.created_at.desc()).limit(limit))
    outputs = result.scalars().all()
    return outputs

# Ensure output directories exist
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = Path(project_root) / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
