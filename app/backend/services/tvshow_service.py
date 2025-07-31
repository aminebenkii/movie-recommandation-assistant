from sqlalchemy.orm import Session
from datetime import date
from functools import partial
from concurrent.futures import ThreadPoolExecutor

from app.backend.core.database import SessionLocal
from app.backend.schemas.tvshow_schemas import TvShowSearchFilters, TvShowCard
from app.backend.models.tvshow_model import CachedTvShow
from app.backend.models.user_media_model import UserMedia
from app.backend.utils.utils import map_genre_to_id, map_id_to_genre
from app.backend.core.tmdb_client import (
    call_tmdb_discover_media_endpoint,
    call_tmdb_media_details_endpoint,
    call_tmdb_media_videos_endpoint,
    call_tmdb_media_id_by_media_name_endpoint,
)
from app.backend.services.llm_service import (
    get_similar_titles_with_llm,
    extract_tvshow_titles_with_llm,
    get_titles_from_description_with_llm,
)
from app.backend.core.omdb_client import call_omdb_client


def fetch_excluded_ids(media_type: str, user_id: int, database: Session) -> set[int]:
    """
    Fetches a set of TMDB IDs for a given user and media type that are marked as
    'seen', 'towatchlater', or 'hidden'. These are excluded from recommendations.
    """
    return {
        row.tmdb_id
        for row in database.query(UserMedia).filter(
            UserMedia.media_type == media_type,
            UserMedia.user_id == user_id,
            UserMedia.status.in_(["seen", "towatchlater", "hidden"]),
        )
    }


def fetch_unseen_tmdb_ids(filters: TvShowSearchFilters, user_id: int, database: Session) -> list[int]:
    """
    Fetch up to 50 TMDB TV shows that:
    - Match the genre filter (genre in position 1 or 2)
    - Have not been marked by the user (seen, later, not_interested)
    """
    max_results = 50
    max_pages = 10
    excluded_ids = fetch_excluded_ids("tv", user_id, database)
    results = []
    page = 1

    while len(results) < max_results and page <= max_pages:
        candidates = call_tmdb_discover_media_endpoint("tv", filters, page)
        for movie in candidates:
            if filters.genre_id is None or filters.genre_id in movie["genre_ids"][:2]:
                if movie["id"] not in excluded_ids:
                    results.append(movie["id"])
                    if len(results) == max_results:
                        break
        page += 1

    return results


def enrich_and_cache_one_tvshow(tmdb_id: int):
    """
    Enrich a single TV show with IMDb rating, vote count, trailer URLs,
    multilingual title/overview, and cache it into the DB.
    Creates its own DB session (thread-safe).
    """
    db = SessionLocal()
    try:
        cached_tvshow = db.query(CachedTvShow).filter(CachedTvShow.tmdb_id == tmdb_id).first()
        if cached_tvshow:
            age = (date.today() - cached_tvshow.cache_update_date).days
            if age <= 7:
                return
            if cached_tvshow.imdb_id:
                imdb_data = call_omdb_client(cached_tvshow.imdb_id)
                cached_tvshow.imdb_rating = float(imdb_data.get("imdb_rating") or 0)
                cached_tvshow.imdb_votes_count = int(imdb_data.get("imdb_votes_count", "0").replace(",", ""))
                cached_tvshow.cache_update_date = date.today()
                db.commit()
        else:
            tmdb_details_en = call_tmdb_media_details_endpoint("tv", tmdb_id, "en")
            tmdb_details_fr = call_tmdb_media_details_endpoint("tv", tmdb_id, "fr")
            imdb_id = tmdb_details_en.get("imdb_id")

            imdb_rating = 0.0
            imdb_votes_count = 0
            if imdb_id:
                imdb_data = call_omdb_client(imdb_id)
                imdb_rating = float(imdb_data.get("imdb_rating") or 0)
                imdb_votes_count = int(imdb_data.get("imdb_votes_count", "0").replace(",", ""))

            genre_ids = [g["id"] for g in tmdb_details_en.get("genres", [])]
            new_tvshow = CachedTvShow(
                tmdb_id=tmdb_id,
                imdb_id=imdb_id,
                imdb_rating=imdb_rating,
                imdb_votes_count=imdb_votes_count,
                release_year=int(tmdb_details_en.get("first_air_date", "0000")[:4]),
                poster_url=(
                    f"https://image.tmdb.org/t/p/original{tmdb_details_en.get('poster_path')}"
                    if tmdb_details_en.get("poster_path") else None
                ),
                title_en=tmdb_details_en.get("name"),
                title_fr=tmdb_details_fr.get("name"),
                genre_ids=genre_ids,
                genre_names_en=[map_id_to_genre("tv", "en", gid) for gid in genre_ids],
                genre_names_fr=[map_id_to_genre("tv", "fr", gid) for gid in genre_ids],
                trailer_url_en=call_tmdb_media_videos_endpoint("tv", tmdb_id, "en"),
                trailer_url_fr=call_tmdb_media_videos_endpoint("tv", tmdb_id, "fr"),
                overview_en=tmdb_details_en.get("overview"),
                overview_fr=tmdb_details_fr.get("overview"),
                cache_update_date=date.today(),
            )
            db.add(new_tvshow)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def enrich_and_cache_tvshows(tmdb_ids: list[int]) -> None:
    """
    Enrich and cache a list of TMDB TV show IDs in parallel.
    Each thread manages its own DB session.
    """
    task = partial(enrich_and_cache_one_tvshow)
    with ThreadPoolExecutor(max_workers=30) as executor:
        executor.map(task, tmdb_ids)


def fetch_tvshows_from_cache(tmdb_ids: list[int], db: Session) -> list[CachedTvShow]:
    """
    Fetches CachedTvShow entries from DB based on tmdb_ids.
    Preserves input order from TMDB.
    """
    if not tmdb_ids:
        return []
    tvshows = db.query(CachedTvShow).filter(CachedTvShow.tmdb_id.in_(tmdb_ids)).all()
    order_map = {tmdb_id: i for i, tmdb_id in enumerate(tmdb_ids)}
    tvshows.sort(key=lambda m: order_map.get(m.tmdb_id, float("inf")))
    return tvshows


def rerank_and_imdb_filter_tvshows(tvshows: list[CachedTvShow], filters: TvShowSearchFilters) -> list[CachedTvShow]:
    """
    Optionally filter and rerank TV shows based on IMDb rating or vote count.
    Falls back to original TMDB order if sort_by is "popularity.desc" or unknown.
    """
    filtered = [
        tv for tv in tvshows
        if (filters.min_imdb_rating is None or tv.imdb_rating > filters.min_imdb_rating)
        and (filters.min_imdb_votes_count is None or tv.imdb_votes_count > filters.min_imdb_votes_count)
    ]

    if filters.sort_by == "vote_average.desc":
        return sorted(filtered, key=lambda tv: tv.imdb_rating or 0.0, reverse=True)[:30]

    if filters.sort_by == "vote_count.desc":
        return sorted(filtered, key=lambda tv: tv.imdb_votes_count or 0, reverse=True)[:30]

    return filtered[:30]


def to_tvshow_card(tvshow: CachedTvShow, language: str) -> TvShowCard:
    """
    Converts a CachedTvShow DB model to a Pydantic TvShowCard,
    using the correct language (EN/FR) for title, overview, genres, and trailer.
    """
    is_french = language == "fr"
    return TvShowCard(
        tmdb_id=tvshow.tmdb_id,
        imdb_id=tvshow.imdb_id,
        title=tvshow.title_fr if is_french else tvshow.title_en,
        genre_names=tvshow.genre_names_fr if is_french else tvshow.genre_names_en,
        release_year=tvshow.release_year,
        imdb_rating=tvshow.imdb_rating,
        imdb_votes_count=tvshow.imdb_votes_count,
        poster_url=tvshow.poster_url,
        trailer_url=tvshow.trailer_url_fr if is_french else tvshow.trailer_url_en,
        overview=tvshow.overview_fr if is_french else tvshow.overview_en,
    )




def recommend_tvshows_by_filters(filters: TvShowSearchFilters, user_id: int, database: Session, language: str) -> list[TvShowCard]:
    """
    Recommends a list of high-quality TV shows that the user hasn't seen,
    based on filters + user history. Pulls from TMDB, enriches with OMDB,
    caches to DB if needed, and returns fully enriched TvShowCards.
    """
    filters.genre_id = map_genre_to_id("tv", "en", filters.genre_name)
    tmdb_ids = fetch_unseen_tmdb_ids(filters, user_id, database)
    enrich_and_cache_tvshows(tmdb_ids)
    cached_tvshows = fetch_tvshows_from_cache(tmdb_ids, database)
    reranked = rerank_and_imdb_filter_tvshows(cached_tvshows, filters)
    return [to_tvshow_card(tv, language) for tv in reranked]


def recommend_similar_tvshows(user_input: str, user_id: int, database: Session, language: str) -> list[TvShowCard]:
    """
    Main entrypoint: LLM-driven similar TV show recommender
    """
    similar_tvshows = get_similar_titles_with_llm("tv", user_input)
    if not similar_tvshows:
        return []

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [
            executor.submit(call_tmdb_media_id_by_media_name_endpoint, "tv", tvshow["title"], tvshow["year"])
            for tvshow in similar_tvshows
        ]
        tmdb_ids = [result for result in (f.result() for f in futures) if result is not None]

    excluded_ids = fetch_excluded_ids("tv", user_id, database)
    filtered_ids = [mid for mid in tmdb_ids if mid not in excluded_ids]
    enrich_and_cache_tvshows(filtered_ids)
    cached_tvshows = fetch_tvshows_from_cache(filtered_ids, database)
    return [to_tvshow_card(tv, language) for tv in cached_tvshows]


def search_tvshows_by_title(user_input: str, database: Session, language: str) -> list[TvShowCard]:
    """
    Main entrypoint: LLM-driven keyword-based TV show search
    """
    matching_tvshows = extract_tvshow_titles_with_llm(user_input)
    if not matching_tvshows:
        return []

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [
            executor.submit(call_tmdb_media_id_by_media_name_endpoint, "tv", tvshow["title"], tvshow["year"])
            for tvshow in matching_tvshows
        ]
        tmdb_ids = [result for result in (f.result() for f in futures) if result is not None]

    enrich_and_cache_tvshows(tmdb_ids)
    cached_tvshows = fetch_tvshows_from_cache(tmdb_ids, database)
    return [to_tvshow_card(tv, language) for tv in cached_tvshows]


def recommend_tvshows_from_description(user_input: str, user_id: int, database: Session, language: str) -> list[TvShowCard]:
    """
    LLM-powered recommendation based on free-form user description of mood, theme, or story (TV shows).
    """
    raw_titles = get_titles_from_description_with_llm("tv", user_input)
    if not raw_titles:
        return []

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [
            executor.submit(call_tmdb_media_id_by_media_name_endpoint, "tv", item["title"], item["year"])
            for item in raw_titles
        ]
        tmdb_ids = [res for res in (f.result() for f in futures) if res is not None]

    excluded_ids = fetch_excluded_ids("tv", user_id, database)
    filtered_ids = [mid for mid in tmdb_ids if mid not in excluded_ids]
    enrich_and_cache_tvshows(filtered_ids)
    cached = fetch_tvshows_from_cache(filtered_ids, database)
    return [to_tvshow_card(tv, language) for tv in cached]
