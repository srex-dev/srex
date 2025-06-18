import json
from typing import Optional, Dict, Any
from datetime import datetime
from . import LLMProvider, LLMProviderFactory
from .base import LLMResponse
from core.services.logging.logger import logger
from core.llm_confidence import score_llm_response

try:
    from langchain_ollama import OllamaLLM
    from langchain.prompts import PromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available. Install with: pip install langchain langchain-ollama")

class LangChainProvider(LLMProvider):
    """LangChain-based LLM provider implementation."""
    
    def __init__(self, model: str, temperature: float = 0.7, base_url: str = "http://localhost:11434"):
        super().__init__(model, temperature)
        self.base_url = base_url.rstrip('/')
        
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain not available. Install with: pip install langchain langchain-ollama")
        
        # Initialize LangChain components
        self.llm = OllamaLLM(
            model=model,
            temperature=temperature,
            base_url=base_url
        )
        
        logger.info(f"✅ Initialized LangChain provider with model: {model}")

    def generate(self, prompt: str, explain: bool = True) -> str:
        """Generate a response using LangChain."""
        try:
            logger.info(f"🚀 LangChain generating response with model: {self.model}")
            
            # Create a simple chain for direct prompt generation
            chain = PromptTemplate.from_template("{input}") | self.llm | StrOutputParser()
            
            # Generate response
            response = chain.invoke({"input": prompt})
            
            if not response or not response.strip():
                logger.warning("⚠️ LangChain response was empty or whitespace.")
                raise ValueError("Empty response from LangChain LLM.")
            
            logger.info("✅ LangChain response received successfully.")
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ LangChain generation error: {e}")
            raise

    def get_available_models(self) -> list[str]:
        """Get list of available models for LangChain provider."""
        # For now, return common Ollama models
        # In the future, this could query the Ollama API through LangChain
        return ["llama2", "mistral", "codellama", "llama2:13b", "llama2:7b"]

    def complete(self, prompt: str, temperature: float = 0.7) -> LLMResponse:
        """Complete a prompt using LangChain."""
        text = self.generate(prompt)
        
        # Determine expected type
        if "rego" in prompt.lower():
            expected_type = "rego"
        elif "json" in prompt.lower():
            expected_type = "json"
        else:
            expected_type = "text"
            
        ai_confidence = score_llm_response(text, expected_type=expected_type)
        
        return LLMResponse(
            text=text,
            model=self.model,
            created_at=datetime.utcnow().isoformat(),
            ai_confidence=ai_confidence
        )

# Register the LangChain provider
if LANGCHAIN_AVAILABLE:
    LLMProviderFactory.register_provider("langchain", LangChainProvider) 