from llm.ollama import generate_with_ollama
from llm.openai import generate_with_openai  # Ensure this file/module exists
from core.logger import logger

def call_llm(prompt: str, explain: bool = True, model: str = "ollama") -> str:
    logger.info(f"🚀 Sending prompt using model: {model}")
    logger.info(f"Prompt (truncated): {prompt[:200]}...")

    try:
        if model == "ollama":
            response = generate_with_ollama(prompt, explain=explain)
        elif model == "openai":
            response = generate_with_openai(prompt, explain=explain)
        else:
            raise ValueError(f"Unsupported model provider: {model}")

        logger.info("✅ LLM response received successfully.")
        return response

    except Exception as e:
        logger.error(f"❌ LLM generation error: {e}")
        raise