from llm.ollama import generate_with_ollama
from core.logger import logger

def call_llm(prompt: str, explain: bool = True) -> str:
    logger.info("🚀 Sending prompt to Ollama...")
    logger.info(f"Prompt (truncated): {prompt[:200]}...")

    try:
        response = generate_with_ollama(prompt, explain=explain)
        logger.info("✅ LLM response received successfully.")
        return response
    except Exception as e:
        logger.error(f"❌ LLM generation error: {e}")
        raise