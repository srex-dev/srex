from typing import Optional
from .providers import LLMProviderFactory
from core.services.logging.logger import logger

def call_llm(
    prompt: str,
    explain: bool = True,
    model: str = "llama2",
    temperature: float = 0.7,
    provider: Optional[str] = None
) -> str:
    """
    Call the LLM with the given prompt and parameters.
    
    Args:
        prompt: The prompt to send to the LLM
        explain: Whether to request an explanation
        model: The model to use (e.g. "llama2", "mistral")
        temperature: The temperature to use
        provider: The provider to use (defaults to 'ollama')
    
    Returns:
        The LLM's response
    """
    provider_name = provider or "ollama"
    llm = LLMProviderFactory.create_provider(
        provider_name,
        model=model,
        temperature=temperature
    )
    logger.info(f"🚀 Sending prompt using model: {model} with temperature={temperature}")
    
    try:
        response = llm.generate(prompt, explain=explain)

        if not response or not response.strip():
            logger.warning("⚠️ LLM response was empty or whitespace.")
            raise ValueError("Empty response from LLM.")

        logger.info("✅ LLM response received successfully.")
        return response

    except Exception as e:
        logger.error(f"❌ LLM generation error: {e}")
        raise

def get_available_models(provider: str = "ollama") -> list[str]:
    """
    Get the list of available models for a provider.
    
    Args:
        provider: The provider to get models for
    
    Returns:
        List of available model names
    """
    llm = LLMProviderFactory.create_provider(provider)
    return llm.get_available_models()

def get_available_providers() -> list[str]:
    """
    Get the list of available providers.
    
    Returns:
        List of available provider names
    """
    return LLMProviderFactory.get_available_providers()