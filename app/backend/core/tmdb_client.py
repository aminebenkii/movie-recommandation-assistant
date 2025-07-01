import requests
from typing import Optional
from app.backend.core.config import TMDB_API_KEY
from app.backend.schemas.movie import MovieSearchFilter


TMDB_BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def get_genres_mapping() -> dict:

    url = f"{TMDB_BASE_URL}/genre/movie/list"
    params = {
        "api_key": TMDB_API_KEY,
        "language" : "en-US"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    # Parse Response:
    data = response.json() 
    genres = data.get("genres", [])

    mapping = {
            "genre_to_id": {genre["name"].lower(): genre["id"] for genre in genres},
            "id_to_genre": {genre["id"]: genre["name"].lower() for genre in genres}
            }
    
    return mapping


def get_imdb_id_from_tmdb(id: int) -> str:

    url = f"{TMDB_BASE_URL}/movie/{id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language" : "en-US"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    # Parse Response:
    data = response.json() 
    
    return data.get("imdb_id")


    
def discover_movies(filters: MovieSearchFilter) -> list[dict]:

    url = f"{TMDB_BASE_URL}/discover/movie"
    all_movies = []
    print("filters :", filters)

    for page in range(1, 4): 

        params = {
            "api_key": TMDB_API_KEY,
            "with_genres": filters.genre_id,
            "primary_release_date.gte": f"{filters.min_release_year}-01-01" if filters.min_release_year else None,
            "with_origin_country": filters.origin_country or None,
            "vote_count.gte": 1000,
            "vote_average.gte": 6,   #  Optional
            "language": filters.response_language or "en-US",
            "sort_by": "vote_average.desc",
            "page": page,
        }

        params = {key: value for key, value in params.items() if value is not None}
        print("params :", params)
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            all_movies.extend(data.get("results", []))
            
        except requests.RequestException:
            continue

    return all_movies




def get_trailers(movie_id : int) -> Optional[str]:

    url = f"{TMDB_BASE_URL}/movie/{movie_id}/videos"
    params = {
        "api_key": TMDB_API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    # Parse Response:
    data = response.json()
    videos = data.get("results", [])

    for video in videos:
        if video["site"] == "YouTube" and video["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={video['key']}"
        
    return None

