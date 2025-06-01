import openai
import os

class OpenAIProvider:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate(self, prompt, **kwargs):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 500),
        )
        return response.choices[0].message["content"].strip()