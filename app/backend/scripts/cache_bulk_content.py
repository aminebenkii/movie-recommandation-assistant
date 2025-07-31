# scripts/cache_bulk_content.py

import time
from datetime import datetime
from itertools import product
import traceback
import requests

from app.backend.core.database import get_db
from app.backend.schemas.movie_schemas import MovieSearchFilters
from app.backend.schemas.tvshow_schemas import TvShowSearchFilters
from app.backend.services.movie_service import recommend_movies_by_filters
from app.backend.services.tvshow_service import recommend_tvshows_by_filters
from sqlalchemy.orm import Session

# 🎯 FULL LIST of genres from schema
MOVIE_GENRES = [
    "action", "adventure", "animation", "comedy", "crime",
    "documentary", "drama", "family", "fantasy", "history",
    "horror", "music", "mystery", "romance", "science fiction",
    "tv movie", "thriller", "war", "western"
]

TVSHOW_GENRES = [
    "action & adventure", "animation", "comedy", "crime", "documentary",
    "drama", "family", "kids", "mystery", "news", "reality",
    "sci-fi & fantasy", "soap", "talk", "war & politics", "western"
]

LANGUAGES = ["en", "fr"]
YEARS = list(range(datetime.now().year, 1979, -1))
SORT_OPTIONS = ["popularity.desc", "vote_average.desc", "vote_count.desc"]
USER_ID = -1

# Filter constants
MIN_RATING = 6.0
MIN_VOTES = 5000
SLEEP_BETWEEN_CALLS = 0.25  # be gentle with TMDB/OMDB

# TMDB and OMDB test endpoints
TMDB_PING = "https://api.themoviedb.org/3/configuration"
OMDB_PING = "http://www.omdbapi.com/?i=tt0133093"


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def check_external_services():
    log("🌍 Checking TMDB and OMDB availability...")
    try:
        tmdb_resp = requests.get(TMDB_PING, timeout=5)
        if tmdb_resp.status_code == 200:
            log("✅ TMDB is reachable.")
        else:
            log(f"⚠️ TMDB status code: {tmdb_resp.status_code}")

        omdb_resp = requests.get(OMDB_PING, timeout=5)
        if omdb_resp.status_code == 200 and "imdbRating" in omdb_resp.text:
            log("✅ OMDB is reachable.")
        else:
            log(f"⚠️ OMDB status code: {omdb_resp.status_code}")

    except Exception as e:
        log(f"❌ External check failed: {e}")


def cache_movies(database: Session):
    log("🚀 Caching MOVIES...")
    total = 0
    combinations = product(MOVIE_GENRES, YEARS, LANGUAGES, SORT_OPTIONS)

    for genre, year, lang, sort in combinations:
        filters = MovieSearchFilters(
            genre_name=genre,
            min_imdb_rating=MIN_RATING,
            min_imdb_votes_count=MIN_VOTES,
            min_release_year=year,
            max_release_year=year,
            original_language=lang,
            sort_by=sort
        )
        try:
            results = recommend_movies_by_filters(filters, USER_ID, database, lang)
            log(f"🎬 {len(results):3} movies | {genre[:12]:<12} | {year} | {lang.upper()} | {sort}")
            total += len(results)
        except Exception as e:
            log(f"❌ Error (MOVIE) [{genre} | {year} | {lang}]: {e}")
            traceback.print_exc()
        time.sleep(SLEEP_BETWEEN_CALLS)

    log(f"✅ Done caching MOVIES. Total added or refreshed: {total}")


def cache_tvshows(database: Session):
    log("📺 Caching TV SHOWS...")
    total = 0
    combinations = product(TVSHOW_GENRES, YEARS, LANGUAGES, SORT_OPTIONS)

    for genre, year, lang, sort in combinations:
        filters = TvShowSearchFilters(
            genre_name=genre,
            min_imdb_rating=MIN_RATING,
            min_imdb_votes_count=MIN_VOTES,
            min_release_year=year,
            max_release_year=year,
            original_language=lang,
            sort_by=sort
        )
        try:
            results = recommend_tvshows_by_filters(filters, USER_ID, database, lang)
            log(f"📺 {len(results):3} shows  | {genre[:16]:<16} | {year} | {lang.upper()} | {sort}")
            total += len(results)
        except Exception as e:
            log(f"❌ Error (TVSHOW) [{genre} | {year} | {lang}]: {e}")
            traceback.print_exc()
        time.sleep(SLEEP_BETWEEN_CALLS)

    log(f"✅ Done caching TV SHOWS. Total added or refreshed: {total}")


if __name__ == "__main__":
    log("🧠 Starting BULK CACHE job...")
    check_external_services()

    db = next(get_db())
    cache_movies(db)
    cache_tvshows(db)

    log("🏁 DONE. You just populated the f*** out of your DB.")
