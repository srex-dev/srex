from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator, Optional

@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    text: str
    model: str
    created_at: Optional[str] = None
    ai_confidence: float = 0.0

class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def complete(self, prompt: str, temperature: float = 0.7) -> LLMResponse:
        """Complete a prompt.
        
        Args:
            prompt: The prompt to complete
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            LLMResponse: The completion response
        """
        pass
    
    @abstractmethod
    def complete_stream(self, prompt: str, temperature: float = 0.7) -> Iterator[LLMResponse]:
        """Stream a completion.
        
        Args:
            prompt: The prompt to complete
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Iterator[LLMResponse]: Stream of completion chunks
        """
        pass 