import requests
from typing import Optional
from app.backend.core.config import TMDB_API_KEY
from app.backend.schemas.movie_schemas import MovieSearchFilters


TMDB_BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def get_genres_mapping(media_type: str, language: str) -> dict:

    url = f"{TMDB_BASE_URL}/genre/{media_type}/list"
    params = {"api_key": TMDB_API_KEY, "language": language}
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


def call_tmdb_discover_media_endpoint(media_type: str, filters: MovieSearchFilters, page: int) -> list[dict]:
    """
    Low-level TMDB client to hit /discover/movie or tv with filter + pagination.
    """
    url = f"{TMDB_BASE_URL}/discover/{media_type}"
    print(f"[DEBUG] Calling TMDB Discover Endpoint: {url}")

    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": filters.genre_id,
        "vote_average.gte": 6,
        "vote_count.gte": 1000,
        "with_original_language": filters.original_language or None,
        "sort_by": filters.sort_by or "popularity.desc",
        "page": page,
    }

    movie_date_filters = {
        "primary_release_date.gte": f"{filters.min_release_year}-01-01" if filters.min_release_year else None,
        "primary_release_date.lte": f"{filters.max_release_year}-12-31" if filters.max_release_year else None,
    }

    tv_date_filters = {
        "first_air_date.gte": f"{filters.min_release_year}-01-01" if filters.min_release_year else None,
        "first_air_date.lte": f"{filters.max_release_year}-12-31" if filters.max_release_year else None,
    }

    # Combine params and strip out None values
    combined_date_filters = movie_date_filters if media_type == "movie" else tv_date_filters
    params.update(combined_date_filters)
    params = {k: v for k, v in params.items() if v is not None}

    print(f"[DEBUG] Final TMDB Discover request params: {params}")

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"[DEBUG] TMDB responded with status code: {response.status_code}")
        response.raise_for_status()

        data = response.json()
        movies = data.get("results", [])
        print(f"[DEBUG] TMDB returned {len(movies)} results on page {page}")
        if not movies:
            print(f"[WARNING] TMDB response was empty. Full payload: {data}")
        return movies

    except requests.RequestException as e:
        print(f"[TMDB ERROR] Discover call failed: {e} | page={page} | params={params}")
        return []


def call_tmdb_media_details_endpoint(media_type: str, tmdb_id: int, language: str) -> dict:
    """
    Given "tv" or "movie", "tmdb_id" and langauge,  it retruns details to enrich.
    """
    url = f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY, "language": language}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if media_type=="tv":
        url = f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/external_ids"
        params = {"api_key": TMDB_API_KEY, "language": language}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data |= response.json()

    return data


def call_tmdb_media_id_by_media_name_endpoint(media_type: str, title: str, year: Optional[int] = None) -> Optional[int]:
    """
    Hits /search/movie on TMDB and tries to return best match TMDB ID.
    """

    url = f"{TMDB_BASE_URL}/search/{media_type}"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
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
        print(f"[TMDB ERROR] Failed to fetch {media_type} ID: {e} | query={title}")
    
    return None
    

def call_tmdb_media_videos_endpoint(media_type: str, tmdb_id: int, language: str) -> Optional[str]:
    """
    Fetches the YouTube trailer URL for a given movie or TV show from TMDB.
    """
    
    url = f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/videos" 
    params = {"api_key": TMDB_API_KEY, "language": language or "en-US"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    videos = data.get("results", [])

    for video in videos:
        if video["site"] == "YouTube" and video["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={video['key']}"

    
    for video in videos:
        if video["site"] == "YouTube" and "trailer" in video["name"].lower():
            return f"https://www.youtube.com/watch?v={video['key']}"
        
    return None


