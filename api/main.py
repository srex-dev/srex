# api/main.py
from fastapi import FastAPI
from api.routes import router
from core.logger import logger

app = FastAPI(
    title="SREx API",
    description="An API for generating and validating SLO YAML files using LLMs.",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 SREx API has started.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 SREx API is shutting down.")

app.include_router(router)