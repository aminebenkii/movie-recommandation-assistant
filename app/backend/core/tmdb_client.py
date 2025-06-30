import requests
from config import TMDB_API_KEY

TMDB_BASE_URL = "https://api.themoviedb.org/3/"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"



def get_genres_mapping() -> dict:

    # Build url
    url = f"{TMDB_BASE_URL}/genre/movie/list"

    # Build params
    params = {
        "api_key" : TMDB_API_KEY,
        "language" : "en-US"
    }

    # Send Request
    response = requests.get(url, params=params)
    response.raise_for_status()

    # Parse response
    data = response.json()
    mapping = {genre["name"].lower(): genre ["id"] for genre in data["genres"]}

    # Return data
    return mapping



def get_genres_reverse_mapping() -> dict:

    # Build url
    url = f"{TMDB_BASE_URL}//genre/movie/list"

    # Build params
    params = {
        "api_key" : TMDB_API_KEY,
        "language" : "en-US"
    }

    # Send Request
    response = requests.get(url, params=params)
    response.raise_for_status()

    # Parse response
    data = response.json()
    mapping = {genre["id"]: genre["name"].lower() for genre in data["genres"]}
    
    # Return data
    return mapping



def discover_movies(filters: dict) -> list:

    # Build url
    url = f"{TMDB_BASE_URL}/discover/movie"

    # Build params
    params = {
        "api_key" : TMDB_API_KEY,
        "language" : "en-US",
        "sort_by": "vote_average_desc",
        "vote_count.gte": filters.get("min_votes", 1000),
        "vote_average.gte": filters.get("min_rating", 7.0),
        "with_genres": filters.get("genre_id"),
        "page": 1
    }

    # Send Request
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    # Parse Response
    data = response.json()
    movies = data.get("results", [])
    # Return data
    
    return movies



def get_trailers(movie_id: int) ->str | None:
    
    # Build url 
    url = f"{TMDB_BASE_URL}/movie/{movie_id}/videos"

    # Build params
    params = {
        "api_key" : TMDB_API_KEY
    }

    # Send Request 
    response = requests.get(url, params=params)
    response.raise_for_status()

    # Parse Response
    data = response.json()
    videos = data.get("results", [])

    for video in videos:
        if video["site"] == "YouTube" and video["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None


