from llm.ollama import generate_with_ollama
from llm.openai import generate_with_openai  # Ensure this file/module exists
from core.logger import logger

def call_llm(prompt: str, explain: bool = True, model: str = "ollama", temperature: float = 0.7) -> str:
    logger.info(f"🚀 Sending prompt using model: {model} with temperature={temperature}")
    
    try:
        if model == "ollama":
            # Pass temperature explicitly to Ollama generator
            response = generate_with_ollama(prompt, explain=explain, temperature=temperature)
        elif model == "openai":
            # Pass temperature explicitly to OpenAI generator
            response = generate_with_openai(prompt, explain=explain, temperature=temperature)
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