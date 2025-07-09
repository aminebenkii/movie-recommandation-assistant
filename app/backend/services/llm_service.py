
from app.backend.core.openai_client import get_openai_completion, build_openai_payload
from app.backend.services.parser_service import parse_filter_line
from app.backend.schemas.movie import MovieCard, MovieSearchFilter
from typing import List, Dict, Tuple, Optional



def get_llm_response(conversation : List[Dict[str, str]]) -> str:
    payload = build_openai_payload(conversation)
    llm_answer = get_openai_completion(payload)
    return llm_answer


def parse_llm_response(llm_response: str) -> Tuple[Optional[str], Optional[MovieSearchFilter], str]:
    lines = llm_response.strip().split("\n")
    filter_line = None
    cleaned_lines = []

    for line in lines:
        if line.startswith("[filters_requested]"):
            filter_line = line  
        else:
            cleaned_lines.append(line)

    action = None
    filter_obj = None

    if filter_line:
        filter_obj = parse_filter_line(filter_line)
        action = "filters_requested"  

    cleaned_llm_output = "\n".join(cleaned_lines).strip()
    return action, filter_obj, cleaned_llm_output


def prune_conversation_for_llm(conversation: List[Dict[str, str]]) -> List[Dict[str, str]]:
    if not conversation:
        return []

    # Find the index of the last "[movie_context]" message
    context_index = None
    for i in reversed(range(len(conversation))):
        msg = conversation[i]
        if "[movie_context]" in msg["content"]:
            context_index = i
            break

    if context_index is None:
        # No [movie_context] → fallback to last 10 messages
        return conversation[-10:]

    # From that context message, grab it and the 3 messages before it
    start_index = max(0, context_index - 3)
    pruned = conversation[start_index:]

    return pruned



def movies_to_overviews_text(movies: List[MovieCard]) -> str:
    
    lines = ["[movie_context]"]

    for i, movie in enumerate(movies, start=1):
        movie_text = (
            f"{i}. Title: {movie.title}, "
            f"IMDb Rating: {movie.imdb_rating}, "
            f"Overview: {movie.overview}"
        )
        lines.append(movie_text)

    return "\n".join(lines)