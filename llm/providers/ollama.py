import json
import requests
from typing import Optional, Dict, Any, Iterator
from datetime import datetime
from . import LLMProvider, LLMProviderFactory
from .base import LLMResponse
from core.services.logging.logger import logger
from core.llm_confidence import score_llm_response

class OllamaProvider(LLMProvider):
    """Ollama LLM provider implementation."""
    
    def __init__(self, model: str, temperature: float = 0.7, base_url: str = "http://localhost:11434"):
        super().__init__(model, temperature)
        self.base_url = base_url.rstrip('/')
        # Verify Ollama is running and accessible
        try:
            response = requests.get(f"{self.base_url}/api/version")
            response.raise_for_status()
            self.version = response.json()["version"]
            logger.info(f"✅ Connected to Ollama version {self.version}")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Ollama service at {self.base_url}: {e}")

    def generate(self, prompt: str, explain: bool = True) -> str:
        """Generate a response from Ollama."""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": 2048,  # Limit response length
                    "stop": ["```", "Human:", "Assistant:"]  # Stop at common conversation markers
                }
            }
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            logger.info(f"📤 Sending request to Ollama at {url}")
            logger.info(f"Model: {self.model}")
            logger.info(f"Headers: {headers}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            # Make the actual request
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=1800  # 30 minute timeout
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response: {json.dumps(data, indent=2)}")
            
            if "response" not in data:
                raise ValueError(f"Unexpected response format from Ollama: {data}")
            
            # Clean up the response to ensure it's just the content
            response_text = data["response"].strip()
            
            # Check if response is already valid JSON (starts with { or [)
            if response_text.startswith("{") or response_text.startswith("["):
                logger.info("✅ LLM returned valid JSON response")
            elif response_text.startswith("Hello") or response_text.startswith("I'm"):
                logger.warning("⚠️ LLM returned conversational response instead of JSON")
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(0)
                    logger.info(f"✅ Extracted JSON from conversational response: {response_text}")
                else:
                    logger.error("❌ Could not extract JSON from conversational response")
                    raise ValueError("LLM returned conversational response instead of JSON")
            else:
                logger.info("✅ LLM response appears to be valid")
            
            return response_text
        except requests.exceptions.Timeout:
            logger.error("Request to Ollama timed out")
            logger.error("This might be due to the model being too slow or the prompt being too complex")
            logger.error("Try reducing the prompt size or using a faster model")
            raise RuntimeError("Request to Ollama timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            logger.error(f"Request URL: {url}")
            logger.error(f"Request headers: {headers}")
            logger.error(f"Request payload: {json.dumps(payload, indent=2)}")
            raise RuntimeError(f"Failed to generate response from Ollama: {e}")
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Invalid response from Ollama: {e}")

    def get_available_models(self) -> list[str]:
        """Get list of available Ollama models."""
        try:
            url = f"{self.base_url}/api/tags"
            headers = {
                "Accept": "application/json"
            }
            logger.info(f"📤 Getting available models from {url}")
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Available models response: {json.dumps(data, indent=2)}")
            
            if "models" not in data:
                raise ValueError(f"Unexpected response format from Ollama: {data}")
            return [model["name"] for model in data["models"]]
        except Exception as e:
            raise RuntimeError(f"Failed to get available models from Ollama: {e}")

    def complete(self, prompt: str, temperature: float = 0.7) -> LLMResponse:
        """Complete a prompt using Ollama."""
        text = self.generate(prompt)
        # Determine expected type
        if "rego" in prompt.lower():
            expected_type = "rego"
        elif "json" in prompt.lower():
            expected_type = "json"
        else:
            expected_type = "rego"
        ai_confidence = score_llm_response(text, expected_type=expected_type)
        return LLMResponse(
            text=text,
            model=self.model,
            created_at=datetime.utcnow().isoformat(),
            ai_confidence=ai_confidence
        )

    def complete_stream(self, prompt: str, temperature: float = 0.7) -> Iterator[LLMResponse]:
        """Stream a completion from Ollama."""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature
                }
            }
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            logger.info(f"📤 Starting stream request to Ollama at {url}")
            logger.info(f"Model: {self.model}")
            logger.info(f"Headers: {headers}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        logger.info(f"Stream chunk: {json.dumps(chunk, indent=2)}")
                        if "response" in chunk:
                            # Determine expected type
                            if "rego" in prompt.lower():
                                expected_type = "rego"
                            elif "json" in prompt.lower():
                                expected_type = "json"
                            else:
                                expected_type = "rego"
                            ai_confidence = score_llm_response(chunk["response"], expected_type=expected_type)
                            yield LLMResponse(
                                text=chunk["response"],
                                model=self.model,
                                created_at=datetime.utcnow().isoformat(),
                                ai_confidence=ai_confidence
                            )
                    except json.JSONDecodeError as e:
                        raise RuntimeError(f"Failed to parse Ollama response: {e}")
        except requests.exceptions.Timeout:
            logger.error("Stream request to Ollama timed out")
            logger.error("This might be due to the model being too slow or the prompt being too complex")
            logger.error("Try reducing the prompt size or using a faster model")
            raise RuntimeError("Stream request to Ollama timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"Stream request failed: {str(e)}")
            logger.error(f"Request URL: {url}")
            logger.error(f"Request headers: {headers}")
            logger.error(f"Request payload: {json.dumps(payload, indent=2)}")
            raise RuntimeError(f"Failed to stream response from Ollama: {e}")

# Register the Ollama provider
LLMProviderFactory.register_provider("ollama", OllamaProvider) 