from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from llm.interface import get_available_models

router = APIRouter()

@router.get("/models")
def get_models(provider: str = Query("ollama", description="LLM provider name")):
    try:
        models = get_available_models(provider)
        return {"models": models}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)}) 