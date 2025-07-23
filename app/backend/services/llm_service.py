from app.backend.core.openai_client import get_openai_completion, build_openai_payload
from app.backend.schemas.movie_schemas import MovieCard, MovieSearchFilters
from typing import List, Dict, Tuple, Optional
import re


def get_llm_response(conversation: List[Dict[str, str]]) -> str:
    payload = build_openai_payload(conversation)
    llm_answer = get_openai_completion(payload)
    return llm_answer


def parse_llm_response(llm_text: str) -> Tuple[str, Optional[str], Optional[str], Optional[MovieSearchFilters]]:
    action = None
    filters = None
    movie_name = None

    # Check for filters
    if "[filters]" in llm_text:
        action = "filters"
        filters_block = llm_text.split("[filters]")[1].strip()
        filters_dict = {}

        for part in filters_block.split(","):
            if "=" not in part:
                continue  # Skip malformed parts
            try:
                key, value = part.strip().split("=", 1)
                filters_dict[key.strip()] = value.strip()
            except Exception:
                continue

        try:
            filters = MovieSearchFilters(**filters_dict)
        except Exception:
            filters = None

    # Check for similar movie block
    elif "[similar_movies]" in llm_text:
        action = "similar_movie"
        match = re.search(r"\[similar_movies\]\s*movie_name\s*=\s*(.+)", llm_text)
        if match:
            movie_name = match.group(1).strip()

    # Clean up assistant message
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
    Always Start with the Actual movie and then make the 49 next ones the similar ones. 
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


def ask_llm_for_matching_keywords_movies(keywords: str) -> list[dict]:
    """
    Ask OpenAI for a list of 50 similar movies with year.
    Returns a list of dicts: {"title": str, "year": int}
    """

    prompt = f"""
        You are a movie search assistant. Based on the user's input keywords, return a clean list of matching movie titles with release years.

        Instructions:
        - Return ONLY a comma-separated list of real movie titles, each with its release year in parentheses.
        - Format: Title (Year), Title (Year), ...
        - If the input is meaningless or contains no relevant movie, return exactly: None
        - If the keywords clearly point to **a single specific movie**, even with typos (e.g. "ge tout"), return just that one movie. Example: Get Out (2017)
        - If the keywords clearly refer to a **franchise** (e.g. "missioni mpossible", "avnegers"), return all entries from that franchise.

        Examples:
        User input: "ge tout"  
        → Output: Get Out (2017)

        User input: "missioni mpossible"  
        → Output: Mission: Impossible (1996), Mission: Impossible 2 (2000), Mission: Impossible III (2006), Mission: Impossible – Ghost Protocol (2011), Mission: Impossible – Rogue Nation (2015), Mission: Impossible – Fallout (2018), Mission: Impossible – Dead Reckoning Part One (2023)

        User input: "blablablablar"  
        → Output: None

        Now process:
        Keywords: "{keywords}"
        """


    payload = [
        {"role": "system", "content": "You are a movie expert."},
        {"role": "user", "content": prompt}
    ]

    llm_answer = get_openai_completion(payload)

    if llm_answer.strip().lower() == "none":
        return []

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
            continue  

    return movie_list


