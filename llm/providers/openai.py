import os
from typing import Optional, Dict, Any
from openai import OpenAI
from . import LLMProvider, LLMProviderFactory
from .base import LLMResponse

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation."""
    
    def __init__(self, model: str, temperature: float = 0.7, api_key: Optional[str] = None):
        super().__init__(model, temperature)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt: str, explain: bool = True) -> str:
        """Generate a response from OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Failed to generate response from OpenAI: {e}")

    def get_available_models(self) -> list[str]:
        """Get list of available OpenAI models."""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            raise RuntimeError(f"Failed to get available models from OpenAI: {e}")

    def complete(self, prompt: str, temperature: float = 0.7) -> LLMResponse:
        text = self.generate(prompt)
        return LLMResponse(text=text, model=self.model)

    def complete_stream(self, prompt: str, temperature: float = 0.7):
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield LLMResponse(text=chunk.choices[0].delta.content, model=self.model)
        except Exception as e:
            raise RuntimeError(f"Failed to stream response from OpenAI: {e}")

# Register the OpenAI provider
LLMProviderFactory.register_provider("openai", OpenAIProvider) 