import os
from openai import OpenAI
from core.services.logging.logger import logger

def generate_with_openai(prompt: str, explain: bool = True, model: str = "gpt-4") -> str:
    api_key = os.getenv("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")  # Use the variable name
    if not api_key:
        raise ValueError("❌ Missing OPENAI_API_KEY environment variable")

    client = OpenAI(api_key=api_key)

    logger.info(f"📡 Calling OpenAI with model={model}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a Site Reliability Engineer (SRE)."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()