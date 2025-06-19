from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.services.prompt.prompt_engine import generate_slo_definitions
from backend.core.logger import logger
import tempfile
import os

router = APIRouter()

class GenerateSLORequest(BaseModel):
    input_yaml: str
    template: str = "base"

@router.get("/health")
async def health_check():
    logger.info("Health check requested.")
    return {"status": "ok"}

@router.post("/generate")
def generate_slo(request: GenerateSLORequest):
    logger.info("Received request to generate SLOs")
    try:
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".yaml") as tmp_input:
            tmp_input.write(request.input_yaml)
            tmp_input_path = tmp_input.name
            logger.debug(f"Temporary input file created at {tmp_input_path}")

        with tempfile.NamedTemporaryFile(delete=False, mode="w+", suffix=".yaml") as tmp_output:
            tmp_output_path = tmp_output.name
            logger.debug(f"Temporary output file created at {tmp_output_path}")

        generate_slo_definitions(
            input_path=tmp_input_path,
            output_path=tmp_output_path,
            template=request.template
        )
        logger.info("SLO generation successful")

        with open(tmp_output_path, "r") as f:
            slo_yaml = f.read()

        # Clean up
        os.remove(tmp_input_path)
        os.remove(tmp_output_path)

        return {"slo_yaml": slo_yaml}
    except Exception as e:
        logger.error(f"Error during SLO generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))