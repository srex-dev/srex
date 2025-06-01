import requests
from core.logger import logger

def generate_with_ollama(prompt: str, explain: bool = True) -> str:
    if explain:
        prompt += "\n\nPlease also explain your reasoning after the YAML."

    try:
        logger.debug("📡 Calling Ollama API at http://localhost:11434/api/generate")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"❌ Failed to connect to Ollama: {e}")
        raise RuntimeError(f"Failed to connect to Ollama: {e}") from e

    try:
        response_data = response.json()
        logger.debug("🧠 Raw Ollama response received.")
        return response_data.get("response", "").strip()
    except Exception as e:
        logger.error(f"❌ Failed to parse Ollama response JSON: {e}")
        logger.debug(f"Raw response content: {response.text}")
        raise RuntimeError("Unable to parse Ollama response") from e