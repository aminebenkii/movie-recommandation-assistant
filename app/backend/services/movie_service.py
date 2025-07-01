from typing import List
from pathlib import Path
from app.backend.core.tmdb_client import discover_movies, get_trailers, get_imdb_id_from_tmdb
from app.backend.core.omdb_client import get_imdb_details
from app.backend.schemas.movie import MovieCard, MovieSearchFilter
from app.backend.utils.utils import read_json
from sqlalchemy.orm import Session
from app.backend.models.seen import SeenMovie


# Mappings File Directory : 
ROOT_DIR = Path(__file__).resolve().parents[3]
MAPPING_FILE_PATH = ROOT_DIR / "data" / "processed" / "genres_mapping.json"

# Load Genre Mapping only once:
GENRE_MAPPING = read_json(MAPPING_FILE_PATH)


def map_genre_to_id(genre : str) -> int:
    mapping = GENRE_MAPPING.get("genre_to_id")
    genre_id = mapping.get(genre.lower().strip())
    if genre_id is None:
        raise ValueError(f"Genre {genre} not found in mapping")
    return genre_id


def map_id_to_genre(id : int) -> str:
    mapping = GENRE_MAPPING.get("id_to_genre")
    genre_name = mapping.get(str(id))
    if genre_name is None:
        raise ValueError(f"Genre with id : {id}, was not found in mapping.")
    return genre_name.lower()


def fetch_seen_movie_ids(user_id: int, database: Session) -> list[int]:
    seen_movies = database.query(SeenMovie).filter(SeenMovie.user_id == user_id).all()
    seen_movies_id_list = [movie.movie_id for movie in seen_movies]
    return seen_movies_id_list


def remove_seen_movies(movies: List[dict], seen_movie_ids: List[int]) -> List[dict]:
    seen_set = set(seen_movie_ids)
    unseen_movies = [movie for movie in movies if movie["id"] not in seen_set]
    return unseen_movies


def enrich_movies_with_imdb(movies: List[dict]) -> List[dict]:

    for movie in movies: 

        imdb_id = get_imdb_id_from_tmdb(movie["id"])

        if not imdb_id:
            continue

        imdb_details = get_imdb_details(imdb_id)

        imdb_rating = imdb_details.get("imdb_rating")
        movie["imdb_rating"] = float(imdb_rating) if imdb_rating else None

        imdb_votes = imdb_details.get("imdb_votes")
        movie["imdb_votes"] = int(imdb_votes.replace(",", "")) if imdb_votes else None

    return movies


def rerank_and_pick_movies(movies: List[dict], filters: MovieSearchFilter, limit: int) -> List[dict]:
    min_rating = filters.min_imdb_rating or 0.0
    min_votes = filters.min_imdb_votes or 0

    filtered = [
        m for m in movies
        if (m.get("imdb_rating") is not None and m.get("imdb_rating") >= min_rating)
        and (m.get("imdb_votes") is not None and m.get("imdb_votes") >= min_votes)
    ]

    reranked = sorted(filtered, key=lambda x: x.get("imdb_rating", 0.0), reverse=True)

    return reranked[:limit]


def enrich_movies_with_trailers(movies: List[dict]) -> List[dict]:
    for movie in movies:
        try:
            trailer_url = get_trailers(movie["id"])
        except Exception as e:
            trailer_url = ""
        movie["trailer_url"] = trailer_url or ""
    return movies


def convert_to_moviecards(movies: List[dict]) -> List[MovieCard]:
    
    cards = []
    for movie in movies:
        cards.append(MovieCard(
            id=movie.get("id"),
            title=movie.get("title") or movie.get("original_title", ""),
            genre_names=[map_id_to_genre(genre_id) for genre_id in movie.get("genre_ids", [])],
            imdb_rating=movie.get("imdb_rating", 0),
            imdb_votes=movie.get("imdb_votes", 0),
            release_year=int(movie.get("release_date")[:4]) if movie.get("release_date") else None,
            poster_url=f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
            trailer_url=movie.get("trailer_url"),
            overview=movie.get("overview", "")
            ))

    return cards


def recommend_movies(filters: MovieSearchFilter, user_id: int, database: Session) -> List[MovieCard]:
    
    # Fill genre ID from name
    filters.genre_id = map_genre_to_id(filters.genre_name)
    print("genre id:", filters.genre_id)

    # Step 1: Discover movies from TMDB
    tmdb_movies = discover_movies(filters)
    if not tmdb_movies:
        return []

    print("Generated movies :", len(tmdb_movies))
    print(tmdb_movies[0])

    # Step 2: Remove movies the user has already seen
    seen_ids = fetch_seen_movie_ids(user_id, database)
    unseen_movies = remove_seen_movies(tmdb_movies, seen_ids)
    print("Unseen movies :", len(unseen_movies))

    # Step 3: Enrich with IMDB ratings and votes
    imdb_enriched_movies = enrich_movies_with_imdb(unseen_movies)

    # Step 4: Rerank and filter based on IMDB criteria
    top_movies = rerank_and_pick_movies(imdb_enriched_movies, filters, limit=10)
    print("top_movies :", len(top_movies))

    # Step 5: Add trailers
    final_movies_data = enrich_movies_with_trailers(top_movies)

    # Step 6: Convert to MovieCard pydantic models
    movie_cards = convert_to_moviecards(final_movies_data)

    return movie_cards




# we will add OMDB Later for real imdb ratings ..... 