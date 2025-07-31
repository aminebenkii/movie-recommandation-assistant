from app.backend.core.config import CHAT_INTENT_CONFIG
from app.backend.core.openai_client import get_openai_completion
import json

def test_chat_intent():
    print("🔎 Type your user query. Type 'exit' to quit.\n")
    
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break

        # Optional: inject media_type manually
        media_type = input("Known media_type? (movie/tv/none): ").strip().lower()
        if media_type not in ("movie", "tv"):
            media_type = None

        # Build conversation
        conversation = [{"role": "user", "content": user_input}]
        if media_type:
            conversation.append({"role": "user", "content": f"The user has selected '{media_type}' as media type."})

        # Call OpenAI
        raw_response = get_openai_completion(
            conversation=conversation,
            prompt=CHAT_INTENT_CONFIG["prompt"],
            temperature=CHAT_INTENT_CONFIG["temperature"]
        )

        print("\n🧠 Raw LLM Response:")
        print(raw_response)

        try:
            if raw_response.startswith("```json"):
                raw_response = raw_response.removeprefix("```json").removesuffix("```").strip()
            elif raw_response.startswith("```"):
                raw_response = raw_response.removeprefix("```").removesuffix("```").strip()
            parsed = json.loads(raw_response)
            print("\n✅ Parsed Result:")
            print(f"- Intent: {parsed['intent']}")
            print(f"- Media Type: {parsed.get('media_type')}")
            print(f"- Message: {parsed['message_to_user']}")
        except Exception as e:
            print("\n❌ Failed to parse JSON:")
            print(str(e))
            print("Original output:\n", raw_response)

        print("\n" + "-"*50 + "\n")


if __name__ == "__main__":
    test_chat_intent()
