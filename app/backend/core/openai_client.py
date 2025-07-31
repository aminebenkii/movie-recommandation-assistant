from openai import OpenAI
from app.backend.core.config import OPENAI_API_KEY, OPENAI_MODEL
from typing import List, Dict

# ─────────────────────────────────────────────
# CLIENT INITIALIZATION
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def get_openai_completion(conversation: List[Dict[str, str]], prompt: str, temperature: float) -> str:

    messages = [{"role": "system", "content": prompt}]
    messages.extend(conversation)

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL, 
            messages=messages, 
            temperature=temperature
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"OpenAI completion failed: {str(e)}")
