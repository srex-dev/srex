# llm/ollama.py

import requests
import json
from core.logger import logger

def generate_with_ollama(prompt: str, explain: bool = True, model: str = "Mistral") -> str:
    """
    Sends a prompt to Ollama with enforced JSON output format.
    Retries once if response is not valid JSON.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt if explain else prompt + "\n\nRespond only with valid JSON.",
        "stream": False,
        "options": {"format": "json"}
    }

    try:
        logger.debug(f"📡 Calling Ollama API: {url}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        response_data = response.json()
        raw_response = response_data.get("response", "").strip()
        logger.debug("🧠 Raw Ollama response received:\n" + raw_response)

        # Try parsing the JSON directly
        try:
            parsed = json.loads(raw_response)
            return raw_response
        except json.JSONDecodeError:
            logger.warning("⚠️ Ollama response is not valid JSON. Retrying with a stricter prompt...")

        # 🔁 Retry with a stripped-down, stricter prompt
        retry_payload = payload.copy()
        retry_payload["prompt"] += "\n\n🛑 STRICT MODE: Respond only with a valid JSON object. Do not add any explanation, commentary, or markdown."
        retry_payload["stream"] = False

        retry_response = requests.post(url, json=retry_payload)
        retry_response.raise_for_status()
        retry_data = retry_response.json()
        retry_raw = retry_data.get("response", "").strip()

        try:
            parsed = json.loads(retry_raw)
            return retry_raw
        except json.JSONDecodeError as e:
            logger.error(f"❌ Retry response is still not valid JSON: {e}")
            logger.info(f"❌ Retry raw response:\n{retry_raw}")
            raise RuntimeError("Ollama failed to return valid JSON after retry.")

    except requests.RequestException as e:
        logger.error(f"❌ Failed to connect to Ollama: {e}")
        raise RuntimeError(f"Failed to connect to Ollama: {e}") from e

    except Exception as e:
        logger.error(f"❌ Unexpected error from Ollama: {e}")
        raise RuntimeError(f"Ollama LLM error: {e}") from e