from typing import Dict, Any, Type
from .base import BaseLLMProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider

class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    def __init__(self):
        self._providers: Dict[str, Type[BaseLLMProvider]] = {
            "ollama": OllamaProvider,
            "openai": OpenAIProvider
        }
    
    def get_available_providers(self) -> list[str]:
        """Get list of available provider types."""
        return list(self._providers.keys())
    
    def create_provider(self, provider_type: str, config: Dict[str, Any]) -> BaseLLMProvider:
        """Create a new LLM provider instance.
        
        Args:
            provider_type: Type of provider to create (e.g. "ollama", "openai")
            config: Configuration dictionary for the provider
            
        Returns:
            BaseLLMProvider: Provider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        if provider_type not in self._providers:
            raise ValueError(f"Unsupported provider type: {provider_type}")
            
        provider_class = self._providers[provider_type]
        return provider_class(**config) 