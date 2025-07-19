from openai import OpenAI
from app.backend.core.config import OPENAI_API_KEY, SYSTEM_PROMPT, OPENAI_MODEL
from typing import List, Dict

# ─────────────────────────────────────────────
# CLIENT INITIALIZATION
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def build_openai_payload(conversation: List[Dict[str, str]]) -> List[Dict[str, str]]:
    messages = []
    messages.append({"role": "system", "content": SYSTEM_PROMPT})
    messages.extend(conversation)
    return messages


def get_openai_completion(messages: List[Dict[str, str]]) -> str:
    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL, messages=messages, temperature=0.3
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"OpenAI completion failed: {str(e)}")
