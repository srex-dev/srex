from llm.ollama import generate_with_ollama
from llm.openai import generate_with_openai  # Ensure this file/module exists
from core.logger import logger

def call_llm(prompt: str, explain: bool = True, model: str = "ollama") -> str:
    logger.info(f"🚀 Sending prompt using model: {model}")
    
    try:
        if model == "ollama":
            # Force json mode inside the backend (handled in ollama.py)
            response = generate_with_ollama(prompt, explain=explain)
        elif model == "openai":
            response = generate_with_openai(prompt, explain=explain)
        else:
            raise ValueError(f"Unsupported model provider: {model}")

        if not response or not response.strip():
            logger.warning("⚠️ LLM response was empty or whitespace.")
            raise ValueError("Empty response from LLM.")

        logger.info("✅ LLM response received successfully.")
        return response

    except Exception as e:
        logger.error(f"❌ LLM generation error: {e}")
        raise