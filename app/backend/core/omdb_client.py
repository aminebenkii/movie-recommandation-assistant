import requests
from app.backend.core.config import OMDB_API_KEY

OMDB_BASE_URL = "http://www.omdbapi.com/"

def get_imdb_details(imdb_id : str) -> dict:

    url = OMDB_BASE_URL
    params = {
        "i": imdb_id,
        "apikey": OMDB_API_KEY,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    return {
        "imdb_rating": data.get("imdbRating", None),
        "imdb_votes": data.get("imdbVotes", None)
    }




