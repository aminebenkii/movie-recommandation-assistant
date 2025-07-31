from typing import List, Dict, Optional

from app.backend.core.openai_client import get_openai_completion
from app.backend.schemas.movie_schemas import MovieSearchFilters
from app.backend.schemas.tvshow_schemas import TvShowSearchFilters
from app.backend.core.config import (
    EXTRACT_TITLE_CONFIG,
    SIMILAR_TITLES_CONFIG,
    FREE_DESCRIPTION_CONFIG,
    FILTER_PARSING_CONFIG,
)

import json


def parse_filters_from_conversation(
    conversation: List[dict],
    media_type: str
) -> Optional[MovieSearchFilters | TvShowSearchFilters]:
    """
    Parses user intent into structured filter criteria using OpenAI.
    """
    prompt = FILTER_PARSING_CONFIG["prompt"][media_type]
    temperature = FILTER_PARSING_CONFIG["temperature"]

    raw = get_openai_completion(conversation, prompt, temperature)

    if raw.startswith("```"):
        raw = raw.strip("```json").strip("```").strip()

    try:
        filters = json.loads(raw)
    except json.JSONDecodeError:
        return None

    if media_type == "movie":
        return MovieSearchFilters(**filters)
    elif media_type == "tv":
        return TvShowSearchFilters(**filters)

    return None


def extract_movie_titles_with_llm(user_input: str) -> List[Dict]:
    """
    Extracts movie titles and release years from user input using LLM.
    """
    messages = [{"role": "user", "content": user_input}]
    prompt = EXTRACT_TITLE_CONFIG["prompt"]["movie"]
    temperature = EXTRACT_TITLE_CONFIG["temperature"]

    raw = get_openai_completion(messages, prompt, temperature)

    if raw.startswith("```"):
        raw = raw.strip("```json").strip("```").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def extract_tvshow_titles_with_llm(user_input: str) -> List[Dict]:
    """
    Extracts TV show titles and release years from user input using LLM.
    """
    messages = [{"role": "user", "content": user_input}]
    prompt = EXTRACT_TITLE_CONFIG["prompt"]["tv"]
    temperature = EXTRACT_TITLE_CONFIG["temperature"]

    raw = get_openai_completion(messages, prompt, temperature)

    if raw.startswith("```"):
        raw = raw.strip("```json").strip("```").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def get_similar_titles_with_llm(media_type: str, user_input: str) -> List[Dict]:
    """
    Uses LLM to suggest titles similar to a given reference movie or TV show.
    """
    messages = [
        {"role": "user", "content": user_input},
        {"role": "user", "content": f"media_type is {media_type}"}
    ]
    prompt = SIMILAR_TITLES_CONFIG["prompt"]
    temperature = SIMILAR_TITLES_CONFIG["temperature"]

    raw = get_openai_completion(messages, prompt, temperature)

    if raw.startswith("```"):
        raw = raw.strip("```json").strip("```").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def get_titles_from_description_with_llm(media_type: str, user_input: str) -> List[Dict]:
    """
    Uses LLM to recommend titles based on free-form description (e.g. "slow burn, mind-bending sci-fi").
    """
    messages = [
        {"role": "user", "content": user_input},
        {"role": "user", "content": f"The user is looking for a {media_type}."}
    ]
    prompt = FREE_DESCRIPTION_CONFIG["prompt"]
    temperature = FREE_DESCRIPTION_CONFIG["temperature"]

    raw = get_openai_completion(messages, prompt, temperature)

    if raw.startswith("```"):
        raw = raw.strip("```json").strip("```").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []
