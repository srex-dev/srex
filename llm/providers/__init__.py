from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, model: str, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature

    @abstractmethod
    def generate(self, prompt: str, explain: bool = True) -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of available models for this provider."""
        pass

class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    _providers: Dict[str, type[LLMProvider]] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: type[LLMProvider]) -> None:
        """Register a new LLM provider."""
        cls._providers[name] = provider_class

    @classmethod
    def create_provider(cls, name: str, **kwargs) -> Optional[LLMProvider]:
        """Create an LLM provider instance."""
        provider_class = cls._providers.get(name)
        if provider_class is None:
            raise ValueError(f"Unknown provider: {name}")
        return provider_class(**kwargs)

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names."""
        return list(cls._providers.keys())

# Import and register providers
from .ollama import OllamaProvider
LLMProviderFactory.register_provider("ollama", OllamaProvider)

# Import LangChain provider if available
try:
    from .langchain_provider import LangChainProvider
    LLMProviderFactory.register_provider("langchain", LangChainProvider)
except ImportError:
    pass  # LangChain provider will register itself if available 