from .openai_provider import OpenAIProvider
from .local_provider import LocalProvider
import os

def get_llm_provider():
    backend = os.getenv("LLM_BACKEND", "local").lower()
    if backend == "openai":
        return OpenAIProvider()
    return LocalProvider()