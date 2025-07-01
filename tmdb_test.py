
from app.backend.services.movie_service import recommend_movies
from app.backend.core.database import SessionLocal
from app.backend.schemas.movie import MovieSearchFilter


db = SessionLocal()

filters = MovieSearchFilter(
    genre_name="thriller",
    min_imdb_rating=6,
    min_imdb_votes=2000,
    min_release_year=2012,
    response_language="en-US"
)

recommended_movies = recommend_movies(filters, user_id=1, database=db)

print(recommended_movies)

for i, movie in enumerate(recommended_movies, 1):
    print(f"\n🎬 Movie {i}")
    print(f"Title        : {movie.title}")
    print(f"Genres       : {', '.join(movie.genre_names)}")
    print(f"Imdb Rating  : {movie.imdb_rating:.1f} ({movie.imdb_votes} votes)")
    print(f"Release Year : {movie.release_year}")
    print(f"Poster URL   : {movie.poster_url}")
    print(f"Trailer URL  : {movie.trailer_url}")
    print(f"Overview     : {movie.overview[:200]}...")  # print only first 200 chars

"""

import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()  # Make sure you have TMDB_API_KEY in your .env file

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def get_tmdb_movie_details(tmdb_id: int):
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"  # Optional, but forces original titles
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"\n🎬 Full TMDB response for TMDB ID {tmdb_id}:\n")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}")

# Example: Inception → TMDB ID = 27205
get_tmdb_movie_details(27205)

"""
