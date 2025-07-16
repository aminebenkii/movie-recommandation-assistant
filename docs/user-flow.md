# 🎬 Movie Flow — `movie_service.py` Implementation

This file describes the actual logic behind the `recommend_movies()` pipeline — implemented using TMDB and OMDB APIs, user-specific filtering, cache enrichment, and IMDb-based reranking. The result is a clean list of Pydantic `MovieCard` objects ready for display.

---

## ✅ Main Function Signature

```python
def recommend_movies(
    filters: MovieSearchFilters,
    user_id: int,
    db: Session,
    language: str
) -> list[MovieCard]
```

---

## 🧭 Pipeline Steps Overview

```python
def recommend_movies(filters, user_id, db, language):
    raw_new_movies = fetch_new_tmdb_movies(filters, user_id, db, language)
    tmdb_ids = enrich_and_cache_movies_to_db(raw_new_movies, language)
    cache_movies = fetch_movies_from_cache(tmdb_ids, db)
    reranked = rerank_movies(cache_movies, filters.sort_by)
    return [to_movie_card(m, language) for m in reranked]
```

---

## 1️⃣ Fetch New TMDB Movies

```python
def fetch_new_tmdb_movies(filters, user_id, db, language) -> list[dict]
```

- Iterates over up to 10 pages of TMDB `/discover/movie` results.
- Keeps only movies where:
  - `filters.genre_id` is in top 2 `genre_ids`
  - TMDB ID is **not** marked as `seen`, `later`, or `not_interested` by the user.

Stops once 30 results are collected.

---

## 2️⃣ Enrich and Cache (Multithreaded)

```python
def enrich_and_cache_movies_to_db(movies: list[dict], language: str) -> list[int]
```

Uses a thread pool:

```python
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(task, movies)
```

Each task runs:

```python
def enrich_and_cache_one_movie_to_db(movie_dict: dict, language: str)
```

### Enrichment Logic Per Movie:

- ✅ If already cached and fresh (≤7 days): skip
- 🔁 If stale: refresh only IMDb rating + vote count from OMDB
- ❌ If not in cache:
  - Get multilingual title + overview from TMDB
  - Get IMDb ID from TMDB
  - Get trailer URLs from TMDB
  - Get IMDb data from OMDB
  - Map genre IDs to names
  - Cache everything in DB

DB sessions are opened and closed **per thread**, with exception handling and rollback safety.

---

## 3️⃣ Retrieve Enriched Movies

```python
def fetch_movies_from_cache(tmdb_ids: list[int], db: Session) -> list[CachedMovie]
```

- Batch fetches all movie records using `tmdb_ids`
- Preserves the original TMDB order using a mapping dict

---

## 4️⃣ Rerank (Based on IMDb Metadata)

```python
def rerank_movies(movies: list[CachedMovie], sort_by: str) -> list[CachedMovie]
```

Supports:

- `"vote_average.desc"` → sort by `imdb_rating`
- `"vote_count.desc"` → sort by `imdb_votes_count`
- `"popularity.desc"` → no reranking (default)

---

## 5️⃣ Convert to `MovieCard` Pydantic Models

```python
def to_movie_card(movie: CachedMovie, language: str) -> MovieCard
```

Uses localized fields:

```python
title = movie.title_fr if language == "fr" else movie.title_en
trailer = movie.trailer_url_fr if language == "fr" else movie.trailer_url_en
overview = movie.overview_fr if language == "fr" else movie.overview_en
genres = movie.genre_names_fr if language == "fr" else movie.genre_names_en
```

Returns:

```python
MovieCard(
    tmdb_id=...,
    title=...,
    genre_names=...,
    release_year=...,
    imdb_rating=...,
    imdb_votes_count=...,
    poster_url=...,
    trailer_url=...,
    overview=...
)
```

---

## ✅ Summary of External API Usage

| API                             | Purpose                            |
|----------------------------------|-------------------------------------|
| TMDB `/discover/movie`           | Get movie candidates                |
| TMDB `/movie/{id}`               | Get title, overview, IMDb ID        |
| TMDB `/movie/{id}/videos`        | Get trailer URLs (EN/FR)            |
| OMDB `?i=imdb_id`                | Get IMDb rating and vote count      |

---

## 🧠 Additional Notes

- ✅ Parallel processing for enrichment = faster UX
- ✅ Cached movies are reused and refreshed weekly
- ✅ Smart filtering eliminates low-relevance results
- ✅ Fully localized `MovieCard` output

---
