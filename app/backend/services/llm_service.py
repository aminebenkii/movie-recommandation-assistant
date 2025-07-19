from app.backend.core.openai_client import get_openai_completion, build_openai_payload
from app.backend.services.parser_service import parse_filter_line
from app.backend.schemas.movie_schemas import MovieCard, MovieSearchFilters
from typing import List, Dict, Tuple, Optional
import re


def get_llm_response(conversation: List[Dict[str, str]]) -> str:
    payload = build_openai_payload(conversation)
    llm_answer = get_openai_completion(payload)
    return llm_answer


def parse_llm_response(llm_text: str) -> Tuple[str, Optional[str], Optional[str], Optional[MovieSearchFilters]]:

    # Defaults
    action = None
    filters = None
    movie_name = None

    # Check for filters
    if "[filters]" in llm_text:
        action = "filters"
        filters_block = llm_text.split("[filters]")[1].strip()

        filters_dict = {}
        for part in filters_block.split(","):
            key, value = part.strip().split("=")
            filters_dict[key.strip()] = value.strip()
            
        filters = MovieSearchFilters(**filters_dict)

    # Check for similar movie
    elif "[similar_movies]" in llm_text:
        action = "similar_movie"
        match = re.search(r"\[similar_movies\]\s*movie_name\s*=\s*(.+)", llm_text)
        if match:
            movie_name = match.group(1).strip()

    # Remove any [filters] or [similar_movies] from final message
    cleaned_text = re.sub(r"\[filters\].*", "", llm_text, flags=re.DOTALL)
    cleaned_text = re.sub(r"\[similar_movies\].*", "", cleaned_text, flags=re.DOTALL)
    cleaned_text = cleaned_text.strip()



    return cleaned_text, action, movie_name, filters


def ask_llm_for_similar_movies(movie_name: str) -> list[dict]:
    """
    Ask OpenAI for a list of 50 similar movies with year.
    Returns a list of dicts: {"title": str, "year": int}
    """

    prompt = f"""
    Return ONLY a comma-separated list of 50 movies similar to "{movie_name}", each with its release year in parentheses.
    Format: Title (Year), Title (Year), ...
    Example: Get Out (2017), Us (2019), The Invitation (2015), Coherence (2013)
    """

    payload = [
        {"role": "system", "content": "You are a movie expert."},
        {"role": "user", "content": prompt}
    ]

    llm_answer = get_openai_completion(payload)

    raw_titles = llm_answer.strip().split(",")

    movie_list = []
    for entry in raw_titles:
        try:
            title, year = entry.strip().rsplit("(", 1)
            movie_list.append({
                "title": title.strip(),
                "year": int(year.replace(")", "").strip())
            })
        except Exception:
            continue  # skip malformed entries

    return movie_list
