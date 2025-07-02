from openai import OpenAI
from app.backend.core.config import OPENAI_API_KEY

# ─────────────────────────────────────────────
# CLIENT INITIALIZATION
openai_client = OpenAI(api_key=OPENAI_API_KEY)

