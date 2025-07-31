from sqlalchemy.orm import Session
from app.backend.core.database import SessionLocal
from datetime import date
from app.backend.schemas.movie_schemas import MovieSearchFilters, MovieCard
from app.backend.models.movie_model import CachedMovie
from app.backend.models.user_media_model import UserMedia
from app.backend.utils.utils import map_genre_to_id, map_id_to_genre
from app.backend.core.tmdb_client import (
    call_tmdb_discover_media_endpoint,
    call_tmdb_media_details_endpoint,
    call_tmdb_media_videos_endpoint,
    call_tmdb_media_id_by_media_name_endpoint,)

from app.backend.services.llm_service import ( 
    get_similar_titles_with_llm, 
    extract_movie_titles_with_llm,
    get_titles_from_description_with_llm

)
from app.backend.core.omdb_client import call_omdb_client
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.exc import IntegrityError
import traceback



def fetch_excluded_ids(media_type: str, user_id: int, database: Session) -> set[int]:
    """
    Fetches a set of TMDB IDs for a given user and media type that are marked as
    'seen', 'towatchlater', or 'hidden'. These are excluded from recommendations.
    """
    excluded_ids = {
        row.tmdb_id
        for row in database.query(UserMedia).filter(
            UserMedia.media_type == media_type,
            UserMedia.user_id == user_id,
            UserMedia.status.in_(["seen", "towatchlater", "hidden"]),
        )
    }
    return excluded_ids


def fetch_unseen_tmdb_ids(filters: MovieSearchFilters, user_id: int, database: Session) -> list[int]:
    """
    Fetch up to 50 TMDB movies that:
    - Match the genre filter (genre in position 1 or 2)
    - Have not been marked by the user (seen, later, not_interested)
    """

    max_results = 50
    max_pages = 10
    excluded_ids = fetch_excluded_ids("movie", user_id, database)
    results = []
    page = 1

    while len(results) < max_results and page <= max_pages:
        candidates = call_tmdb_discover_media_endpoint("movie", filters, page)
        for movie in candidates:
            if filters.genre_id is None or filters.genre_id in movie["genre_ids"][:2]:
                if movie["id"] not in excluded_ids:
                    results.append(movie["id"])
                    if len(results) == max_results:
                        break

        page += 1

    return results


def enrich_and_cache_one_movie(tmdb_id: int):
    """
    Enrich a single movie with IMDb rating, vote count, trailer URLs,
    multilingual title/overview, and cache it into the DB.
    Each thread has its own DB session (thread-safe).
    """
    db = SessionLocal()

    try:
        cached_movie = db.query(CachedMovie).filter(CachedMovie.tmdb_id == tmdb_id).first()
        freshly_cached = cached_movie and (date.today() - cached_movie.cache_update_date).days <= 7

        if cached_movie:
            if not freshly_cached:
                imdb_data = call_omdb_client(cached_movie.imdb_id)
                cached_movie.imdb_rating = float(imdb_data.get("imdb_rating") or 0)
                cached_movie.imdb_votes_count = int(imdb_data.get("imdb_votes_count", "0").replace(",", ""))
                cached_movie.cache_update_date = date.today()
                db.commit()
        else:
            tmdb_details_en = call_tmdb_media_details_endpoint("movie", tmdb_id, "en")
            tmdb_details_fr = call_tmdb_media_details_endpoint("movie", tmdb_id, "fr")
            imdb_data = call_omdb_client(tmdb_details_en["imdb_id"])
            genre_ids = tmdb_details_en.get("genre_ids", [])

            new_movie = CachedMovie(
                tmdb_id=tmdb_id,
                imdb_id=tmdb_details_en["imdb_id"],
                imdb_rating=float(imdb_data.get("imdb_rating") or 0),
                imdb_votes_count=int(imdb_data.get("imdb_votes_count", "0").replace(",", "")),
                release_year=int(tmdb_details_en.get("release_date", "0000")[:4]),
                poster_url=(f"https://image.tmdb.org/t/p/original{tmdb_details_en.get('poster_path')}" if tmdb_details_en.get("poster_path") else None),
                title_en=tmdb_details_en.get("title"),
                title_fr=tmdb_details_fr.get("title"),
                genre_ids=genre_ids,
                genre_names_en=[map_id_to_genre("movie", "en", gid) for gid in genre_ids],
                genre_names_fr=[map_id_to_genre("movie", "fr", gid) for gid in genre_ids],
                trailer_url_en=call_tmdb_media_videos_endpoint("movie", tmdb_id, "en"),
                trailer_url_fr=call_tmdb_media_videos_endpoint("movie", tmdb_id, "fr"),
                overview_en=tmdb_details_en.get("overview"),
                overview_fr=tmdb_details_fr.get("overview"),
                cache_update_date=date.today(),
            )

            try:
                db.add(new_movie)
                db.commit()
            except IntegrityError:
                db.rollback()
    except Exception:
        db.rollback()
    finally:
        db.close()


def enrich_and_cache_movies(tmdb_ids: list[int]) -> None:
    """
    Enrich and cache a list of TMDB movie IDs in parallel.
    Each thread manages its own DB session.
    """
    task = partial(enrich_and_cache_one_movie)

    with ThreadPoolExecutor(max_workers=30) as executor:
        executor.map(task, tmdb_ids)


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
        imdb_id=movie.imdb_id,
        title=movie.title_fr if is_french else movie.title_en,
        genre_names=movie.genre_names_fr if is_french else movie.genre_names_en,
        release_year=movie.release_year,
        imdb_rating=movie.imdb_rating,
        imdb_votes_count=movie.imdb_votes_count,
        poster_url=movie.poster_url,
        trailer_url=movie.trailer_url_fr if is_french else movie.trailer_url_en,
        overview=movie.overview_fr if is_french else movie.overview_en,
    )




def recommend_movies_by_filters(filters: MovieSearchFilters, user_id: int, database: Session, language: str) -> list[MovieCard]:
    """
    Recommends a list of high-quality movies that the user hasn't seen,
    based on filters + User history. Pulls from TMDB, enriches with OMDB,
    caches to DB if needed, and returns fully enriched MovieCards.
    """

    filters.genre_id = map_genre_to_id("movie", "en", filters.genre_name)
    tmdb_ids = fetch_unseen_tmdb_ids(filters, user_id, database)
    enrich_and_cache_movies(tmdb_ids)
    cache_movies = fetch_movies_from_cache(tmdb_ids, database)
    reranked = rerank_and_imdb_filter_movies(cache_movies, filters)
    return [to_movie_card(m, language) for m in reranked]


def recommend_similar_movies(user_input: str, user_id: int, database: Session, language: str) -> list[MovieCard]:
    similar_movies = get_similar_titles_with_llm("movie", user_input)
    if not similar_movies:
        return []

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [
            executor.submit(call_tmdb_media_id_by_media_name_endpoint, "movie", movie["title"], movie["year"])
            for movie in similar_movies
        ]
        tmdb_ids = [result for result in (f.result() for f in futures) if result is not None]

    if not tmdb_ids:
        return []

    excluded_ids = fetch_excluded_ids("movie", user_id, database)
    filtered_ids = [mid for mid in tmdb_ids if mid not in excluded_ids]

    if not filtered_ids:
        return []

    enrich_and_cache_movies(filtered_ids)
    cached_movies = fetch_movies_from_cache(filtered_ids, database)
    return [to_movie_card(m, language) for m in cached_movies]


def search_movies_by_title(user_input: str, database: Session, language: str) -> list[MovieCard]:
    matching_movies = extract_movie_titles_with_llm(user_input)
    if not matching_movies:
        return []

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [
            executor.submit(call_tmdb_media_id_by_media_name_endpoint, "movie", movie["title"], movie["year"])
            for movie in matching_movies
        ]
        tmdb_ids = [result for result in (f.result() for f in futures) if result is not None]

    enrich_and_cache_movies(tmdb_ids)
    cached_movies = fetch_movies_from_cache(tmdb_ids, database)
    return [to_movie_card(m, language) for m in cached_movies]


def recommend_movies_from_description(user_input: str, user_id: int, database: Session, language: str) -> list[MovieCard]:
    raw_titles = get_titles_from_description_with_llm("movie", user_input)
    if not raw_titles:
        return []

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [
            executor.submit(call_tmdb_media_id_by_media_name_endpoint, "movie", item["title"], item["year"])
            for item in raw_titles
        ]
        tmdb_ids = [res for res in (f.result() for f in futures) if res is not None]

    excluded_ids = fetch_excluded_ids("movie", user_id, database)
    filtered_ids = [mid for mid in tmdb_ids if mid not in excluded_ids]

    enrich_and_cache_movies(filtered_ids)
    cached = fetch_movies_from_cache(filtered_ids, database)
    return [to_movie_card(m, language) for m in cached]
