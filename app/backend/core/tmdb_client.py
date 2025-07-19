import requests
from typing import Optional
from app.backend.core.config import TMDB_API_KEY
from app.backend.schemas.movie_schemas import MovieSearchFilters


TMDB_BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def get_genres_mapping() -> dict:

    url = f"{TMDB_BASE_URL}/genre/movie/list"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    response.raise_for_status()

    # Parse Response:
    data = response.json()
    genres = data.get("genres", [])

    mapping = {
        "genre_to_id": {genre["name"].lower(): genre["id"] for genre in genres},
        "id_to_genre": {genre["id"]: genre["name"].lower() for genre in genres},
    }

    return mapping


def call_tmdb_movie_details_endpoint(id: int, language: str) -> dict:

    url = f"{TMDB_BASE_URL}/movie/{id}"
    params = {"api_key": TMDB_API_KEY, "language": language}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    return data


def call_tmdb_discover_movies_endpoint(filters: MovieSearchFilters, page: int) -> list[dict]:
    """
    Low-level TMDB client to hit /discover/movie with filter + pagination.
    """

    url = f"{TMDB_BASE_URL}/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": filters.genre_id,
        "vote_average.gte": 6,
        "vote_count.gte": 1000,
        "primary_release_date.gte": (
            f"{filters.min_release_year}-01-01" if filters.min_release_year else None
        ),
        "primary_release_date.lte": (
            f"{filters.max_release_year}-01-01" if filters.max_release_year else None
        ),
        "with_original_language": filters.original_language or None,
        "sort_by": filters.sort_by or "popularity.desc",
        "page": page,
    }
    params = {key: value for key, value in params.items() if value is not None}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        movies = data.get("results", [])
        return movies

    except requests.RequestException as e:
        print(f"[TMDB ERROR] Discover call failed: {e} | page={page} | params={params}")
        return []


def call_tmdb_movie_id_by_movie_name_endpoint(movie_title: str, year: Optional[int] = None) -> Optional[int]:
    """
    Hits /search/movie on TMDB and tries to return best match TMDB ID.
    """

    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": movie_title,
        "include_adult": False,
    }
    if year:
        params["year"] = year

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if results:
            return results[0]["id"]
    except requests.RequestException as e:
        print(f"[TMDB ERROR] Failed to fetch movie ID: {e} | query={movie_title}")
    
    return None
    

def call_tmdb_similar_movies_endpoint(tmdb_id: str, language: str, page: int) -> list[dict]:
    """
    Low-level TMDB client to hit /movie/similar with tmdb_id + pagination.
    """

    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}/similar"
    params = {
        "api_key": TMDB_API_KEY,
        "language": language,
        "page": page,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        movies = data.get("results", [])
        return movies

    except requests.RequestException as e:
        print(f"[TMDB ERROR] Similar call failed: {e} | page={page} | params={params}")
        return []


def call_tmdb_movie_videos_endpoint(movie_id: int, language: str) -> Optional[str]:

    url = f"{TMDB_BASE_URL}/movie/{movie_id}/videos"
    params = {"api_key": TMDB_API_KEY, "language": language or "en-US"}
    response = requests.get(url, params=params)
    response.raise_for_status()

    # Parse Response:
    data = response.json()
    videos = data.get("results", [])

    for video in videos:
        if video["site"] == "YouTube" and video["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={video['key']}"

    return None


