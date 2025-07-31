from sqlalchemy.orm import Session
from app.backend.models.user_model import User
from app.backend.schemas.chat_schemas import ChatQuery, ChatResponse
from typing import Optional

from app.backend.core.openai_client import get_openai_completion
from app.backend.services.session_service import get_or_create_chat_session

from app.backend.services.movie_service import (
    recommend_movies_by_filters, 
    recommend_movies_from_description,
    recommend_similar_movies, 
    search_movies_by_title,
)
from app.backend.services.tvshow_service import(
    recommend_tvshows_by_filters, 
    recommend_tvshows_from_description,
    recommend_similar_tvshows, 
    search_tvshows_by_title,
)

from app.backend.services.llm_service import parse_filters_from_conversation

from app.backend.core.config import CHAT_INTENT_CONFIG
import json


def process_chat_query(payload: ChatQuery, user: User, database: Session, language: str) -> ChatResponse:
    """
    Main entry point for processing a chat query from the frontend.
    Determines the user’s intent and routes the query accordingly.
    """

    # 1. Get or create chat session
    chat_session = get_or_create_chat_session(user.id, payload.session_id, database)

    # 2. Append user's message to session
    chat_session.conversation.append({"role": "user", "content": payload.query})

    # 3. Prune to last 2 exchanges (max 4 messages)
    pruned_conversation = chat_session.conversation[-4:]

    # 4. Classify intent using LLM
    try:
        intent, media_type, msg_for_user = answer_and_classify_user_intent(pruned_conversation, getattr(payload, "media_type", None))
    except Exception:
        return ChatResponse(message="Internal server error while understanding your request.")

    # 5. Route by intent
    match intent:
        case "error":
            return ChatResponse(message=msg_for_user, media_type=None)

        case "exact_title":
            if media_type == "movie":
                results = search_movies_by_title(payload.query, database, language)
            else:
                results = search_tvshows_by_title(payload.query, database, language)
            return ChatResponse(message=msg_for_user, results=results, media_type=media_type)

        case "similar_media":
            if media_type == "movie":
                results = recommend_similar_movies(payload.query, user.id, database, language)
            else:
                results = recommend_similar_tvshows(payload.query, user.id, database, language)
            return ChatResponse(message=msg_for_user, results=results, media_type=media_type)

        case "filters_parsing":
            filters = parse_filters_from_conversation(pruned_conversation, media_type)
            if media_type == "movie":
                results = recommend_movies_by_filters(filters, user.id, database, language)
            else:
                results = recommend_tvshows_by_filters(filters, user.id, database, language)
            return ChatResponse(message=msg_for_user, results=results, filters=filters, media_type=media_type)

        case "free_description_suggestion":
            if media_type == "movie":
                results = recommend_movies_from_description(payload.query, user.id, database, language)
            else:
                results = recommend_tvshows_from_description(payload.query, user.id, database, language)
            return ChatResponse(message=msg_for_user, results=results, media_type=media_type)

    return ChatResponse(message="Something went wrong. Please try again.")


def answer_and_classify_user_intent(conversation: list[dict], media_type: Optional[str]):
    """
    Calls the OpenAI LLM to classify the user intent and optionally extract filters.
    """
    if media_type:
        conversation.append({
            "role": "user",
            "content": f"The user has selected '{media_type}' as media type."
        })

    raw_response = get_openai_completion(
        conversation=conversation,
        prompt=CHAT_INTENT_CONFIG["prompt"],
        temperature=CHAT_INTENT_CONFIG["temperature"]
    )

    try:
        # Clean formatting from OpenAI
        if raw_response.startswith("```json"):
            raw_response = raw_response.removeprefix("```json").removesuffix("```").strip()
        elif raw_response.startswith("```"):
            raw_response = raw_response.removeprefix("```").removesuffix("```").strip()

        parsed = json.loads(raw_response)
        return (
            parsed["intent"],
            parsed.get("media_type"),
            parsed["message_to_user"]
        )
    except Exception as e:
        raise ValueError(f"Failed to parse LLM response: {raw_response}") from e
