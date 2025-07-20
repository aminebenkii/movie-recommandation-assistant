from sqlalchemy.orm import Session
from app.backend.core.database import SessionLocal
from datetime import date
from app.backend.schemas.movie_schemas import MovieSearchFilters, MovieCard
from app.backend.models.movie_model import CachedMovie
from app.backend.models.user_movie_model import UserMovie
from app.backend.utils.utils import map_genre_to_id, map_id_to_genre
from app.backend.core.tmdb_client import (
    call_tmdb_discover_movies_endpoint,
    call_tmdb_movie_details_endpoint,
    call_tmdb_movie_videos_endpoint,
    call_tmdb_movie_id_by_movie_name_endpoint,
)

from app.backend.services.llm_service import ask_llm_for_similar_movies
from app.backend.core.omdb_client import call_omdb_client
from functools import partial
from concurrent.futures import ThreadPoolExecutor




def recommend_movies(filters: MovieSearchFilters, user_id: int, database: Session, language: str) -> list[MovieCard]:
    """
    Recommends a list of high-quality movies that the user hasn't seen,
    based on filters + User history. Pulls from TMDB, enriches with OMDB,
    caches to DB if needed, and returns fully enriched MovieCards.
    """

    filters.genre_id = map_genre_to_id(filters.genre_name)

    tmdb_ids = fetch_unseen_tmdb_ids(filters, user_id, database)

    get_and_cache_movies_data_to_db(tmdb_ids)

    cache_movies = fetch_movies_from_cache(tmdb_ids, database)

    reranked = rerank_and_imdb_filter_movies(cache_movies, filters)

    movie_cards = [to_movie_card(m, language) for m in reranked]

    return movie_cards


def fetch_unseen_tmdb_ids(filters: MovieSearchFilters, user_id: int, db: Session) -> list[int]:
    """
    Fetch up to 30 TMDB movies that:
    - Match the genre filter (genre in position 1 or 2)
    - Have not been marked by the user (seen, later, not_interested)
    """

    excluded_ids = {
        row.tmdb_id
        for row in db.query(UserMovie).filter(
            UserMovie.user_id == user_id,
            UserMovie.status.in_(["seen", "later", "hidden"]),
        )
    }

    results = []
    page = 1

    while len(results) < 60 and page <= 40:
        candidates = call_tmdb_discover_movies_endpoint(filters, page)
        for movie in candidates:
            if filters.genre_id is None or filters.genre_id in movie["genre_ids"][:2]:
                if movie["id"] not in excluded_ids:
                    results.append(movie["id"])
                    if len(results) == 60:
                        break

        page += 1

    return results


def get_and_cache_one_movie_data_to_db(tmdb_id):
    """
    Enrich a single movie with IMDb rating, vote count, trailer URLs,
    multilingual title/overview, and cache it into the DB.
    Creates its own DB session (thread-safe).
    """
    db = SessionLocal()
    try:

        cached_movie = db.query(CachedMovie).filter(CachedMovie.tmdb_id == tmdb_id).first()
        freshly_cached = cached_movie and (date.today() - cached_movie.cache_update_date).days <= 7
    
        if cached_movie:
            if not freshly_cached:
                imdb_data = call_omdb_client(cached_movie.imdb_id)
                cached_movie.imdb_rating = float(imdb_data.get("imdb_rating") or 0)
                cached_movie.imdb_votes_count = int(
                    imdb_data.get("imdb_votes_count", "0").replace(",", "")
                )
                cached_movie.cache_update_date = date.today()
                db.commit()

        else:

            # Fetch from TMDB & OMDB in opposite language
            
            tmdb_details_en = call_tmdb_movie_details_endpoint(tmdb_id, "en")
            tmdb_details_fr = call_tmdb_movie_details_endpoint(tmdb_id, "fr")

            imdb_data = call_omdb_client(tmdb_details_en["imdb_id"])
            genre_ids = tmdb_details_en.get("genre_ids", [])

            new_movie = CachedMovie(
                tmdb_id=tmdb_id,
                imdb_id=tmdb_details_en["imdb_id"],

                imdb_rating=float(imdb_data.get("imdb_rating") or 0),
                imdb_votes_count=int(
                    imdb_data.get("imdb_votes_count", "0").replace(",", "")
                ),
                release_year=int(tmdb_details_en.get("release_date", "0000")[:4]),

                poster_url=(
                    f"https://image.tmdb.org/t/p/original{tmdb_details_en.get('poster_path')}"
                    if tmdb_details_en.get("poster_path")
                    else None
                ),

                title_en=tmdb_details_en.get("title"),
                title_fr=tmdb_details_fr.get("title"),

                genre_ids=genre_ids,
                genre_names_en=[map_id_to_genre(gid, "en") for gid in genre_ids],
                genre_names_fr=[map_id_to_genre(gid, "fr") for gid in genre_ids],

                trailer_url_en=call_tmdb_movie_videos_endpoint(tmdb_id, "en"),
                trailer_url_fr=call_tmdb_movie_videos_endpoint(tmdb_id, "fr"),

                overview_en=tmdb_details_en.get("overview"),
                overview_fr=tmdb_details_fr.get("overview"),

                cache_update_date=date.today(),
            )

            db.add(new_movie)
            db.commit()

    except Exception as e:
        print(f"[Thread] Error caching TMDB ID {tmdb_id}: {e}")
        db.rollback()
    finally:
        db.close()


def get_and_cache_movies_data_to_db(movies: list[dict]) -> list[int]:
    """
    Enrich and cache a list of movies in parallel (IMDb, trailer, genres).
    Each thread manages its own DB session.
    Returns the list of tmdb_ids that were processed.
    """
    task = partial(get_and_cache_one_movie_data_to_db)

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(task, movies)

    return None


def fetch_movies_from_cache(tmdb_ids: list[int], db: Session) -> list[CachedMovie]:
    """
    Fetches CachedMovie entries from DB based on tmdb_ids.
    Preserves input order from TMDB.
    """
    if not tmdb_ids:
        return []

    # 1. Batch query
    movies = db.query(CachedMovie).filter(CachedMovie.tmdb_id.in_(tmdb_ids)).all()

    # 2. Preserve input order
    order_map = {tmdb_id: i for i, tmdb_id in enumerate(tmdb_ids)}
    movies.sort(key=lambda m: order_map.get(m.tmdb_id, float("inf")))

    return movies


def rerank_and_imdb_filter_movies(movies: list[CachedMovie], filters: MovieSearchFilters) -> list[CachedMovie]:
    """
    Optionally rerank movies based on IMDb rating or vote count.
    Falls back to original TMDB order if sort_by is "popularity.desc".
    """
    
    movies = [
        movie for movie in movies
        if (filters.min_imdb_rating is None or movie.imdb_rating > filters.min_imdb_rating)
        and (filters.min_imdb_votes_count is None or movie.imdb_votes_count > filters.min_imdb_votes_count)
    ]

    if filters.sort_by == "vote_average.desc":
        return sorted(movies, key=lambda m: m.imdb_rating or 0.0, reverse=True)[:30]

    if filters.sort_by == "vote_count.desc":
        return sorted(movies, key=lambda m: m.imdb_votes_count or 0, reverse=True)[:30]

    # "popularity.desc" or unknown sort → no reranking
    return movies[:30]


def to_movie_card(movie: CachedMovie, language: str) -> MovieCard:
    """
    Converts a CachedMovie DB model to a Pydantic MovieCard,
    using the correct language (EN/FR) for title, overview, genres, and trailer.
    """
    is_french = language == "fr"

    return MovieCard(
        tmdb_id=movie.tmdb_id,
        title=movie.title_fr if is_french else movie.title_en,
        genre_names=movie.genre_names_fr if is_french else movie.genre_names_en,
        release_year=movie.release_year,
        imdb_rating=movie.imdb_rating,
        imdb_votes_count=movie.imdb_votes_count,
        poster_url=movie.poster_url,
        trailer_url=movie.trailer_url_fr if is_french else movie.trailer_url_en,
        overview=movie.overview_fr if is_french else movie.overview_en,
    )










def recommend_similar_movies(movie_name: str, user_id: int, db: Session, language: str) -> list[MovieCard]:
    """
    Main entrypoint: LLM-driven similar movie recommender
    """

    # 1. Ask LLM for 50 semantically similar movie titles
    similar_movies = ask_llm_for_similar_movies(movie_name)

    if not similar_movies:
        print(f"[LLM WARNING] No movies returned for: {movie_name}")
        return []

    # 2. Lookup TMDB IDs from titles and years
    tmdb_ids = []
    for movie in similar_movies:
        tmdb_id = call_tmdb_movie_id_by_movie_name_endpoint(movie["title"], movie["year"])
        if tmdb_id:
            tmdb_ids.append(tmdb_id)

    # 3. Filter out movies the user has already seen / saved
    excluded_ids = {
        row.tmdb_id
        for row in db.query(UserMovie).filter(
            UserMovie.user_id == user_id,
            UserMovie.status.in_(["seen", "later", "hidden"]),
        )
    }
    filtered_ids = [mid for mid in tmdb_ids if mid not in excluded_ids]

    # 4. Cache and enrich movie metadata
    get_and_cache_movies_data_to_db(filtered_ids)

    # 5. Fetch from cache and return movie cards
    cached_movies = fetch_movies_from_cache(filtered_ids, db)
    return [to_movie_card(m, language) for m in cached_movies]
