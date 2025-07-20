# 🎬 Movie Flow — `movie_service.py`

This document describes the two main recommendation flows in the backend:

- `recommend_movies()` → classic filter-based discovery  
- `recommend_similar_movies()` → LLM-powered similarity-based discovery

Both functions return localized, high-quality `MovieCard` results by:
- Fetching TMDB movie IDs
- Enriching metadata with TMDB + OMDB
- Caching results in the database
- Filtering out seen / hidden movies
- Returning clean results in EN or FR

---

## 🔧 Function 1: `recommend_movies()`  
Manual filtering flow

```
def recommend_movies(filters: MovieSearchFilters, user_id: int, db: Session, language: str) -> list[MovieCard]
```

### 📥 Inputs:
- `filters`: genre, IMDb rating, votes, year, etc.
- `user_id`: to exclude seen/later/not_interested
- `db`: SQLAlchemy session
- `language`: "en" or "fr"

---

### 🔁 Step-by-Step:

#### 1. Fetch up to 60 unseen TMDB movie IDs

```
tmdb_ids = fetch_unseen_tmdb_ids(filters, user_id, db)
```

- Calls TMDB’s `/discover/movie` page-by-page
- Keeps only:
  - Movies where `genre_id` is 1st or 2nd in `genre_ids`
  - Movies not marked by user (seen, later, hidden)

---

#### 2. Enrich and cache metadata

```
get_and_cache_movies_data_to_db(tmdb_ids)
```

- For each TMDB ID:
  - Checks if cached and fresh (≤ 7 days)
  - If stale → updates IMDb data
  - If missing → fetches:
    - EN + FR title, overview, trailer
    - IMDb rating and vote count
    - Genre names (mapped from ID)

Multithreaded with safe DB sessions.

---

#### 3. Load enriched movies from cache

```
cached_movies = fetch_movies_from_cache(tmdb_ids, db)
```

- Preserves the original TMDB order

---

#### 4. Apply optional reranking (IMDb)

```
reranked = rerank_and_imdb_filter_movies(cached_movies, filters)
```

- Filters by:
  - `min_imdb_rating`
  - `min_imdb_votes_count`
- Sorts by:
  - `"vote_average.desc"` → IMDb rating
  - `"vote_count.desc"` → IMDb votes
  - `"popularity.desc"` → No reranking (default)

---

#### 5. Convert to `MovieCard` objects

```
return [to_movie_card(movie, language) for movie in reranked]
```

- Uses localized title, trailer, genres, and overview

---

## 🧠 Function 2: `recommend_similar_movies()`  
LLM-driven similarity-based flow

```
def recommend_similar_movies(movie_name: str, user_id: int, db: Session, language: str) -> list[MovieCard]
```

### 📥 Inputs:
- `movie_name`: base movie to match against
- `user_id`: to avoid duplicates
- `db`: database session
- `language`: output language ("en" or "fr")

---

### 🔁 Step-by-Step:

#### 1. Ask OpenAI for similar movie titles

```
similar_movies = ask_llm_for_similar_movies(movie_name)
```

Returns a list like:

```
[{"title": "Enemy", "year": 2013}, {"title": "The Lobster", "year": 2015}]
```

---

#### 2. Resolve titles to TMDB IDs

```
tmdb_ids = [
    call_tmdb_movie_id_by_movie_name_endpoint(title, year)
    for title, year in similar_movies
]
```

---

#### 3. Filter out movies already seen or hidden

```
excluded_ids = get_user_excluded_tmdb_ids(user_id, db)
filtered_ids = [id for id in tmdb_ids if id not in excluded_ids]
```

---

#### 4. Enrich and cache metadata

```
get_and_cache_movies_data_to_db(filtered_ids)
```

---

#### 5. Fetch from cache and return `MovieCard`s

```
cached_movies = fetch_movies_from_cache(filtered_ids, db)
return [to_movie_card(m, language) for m in cached_movies]
```

---

## 📦 Enrichment & Caching Logic (Shared)

```
get_and_cache_movies_data_to_db(tmdb_ids)
```

→ uses threads to run:

```
get_and_cache_one_movie_data_to_db(tmdb_id)
```

Each movie:
- Checks if already cached and fresh
- Refreshes IMDb only if stale
- Fully populates fields if missing:
  - `title_en`, `title_fr`
  - `overview_en`, `overview_fr`
  - `trailer_url_en`, `trailer_url_fr`
  - `imdb_rating`, `imdb_votes_count`
  - `genre_names_en`, `genre_names_fr`
- Saves to DB via `CachedMovie` model

---

## 🎬 `MovieCard` Output Model

Both functions return:

```
MovieCard(
    tmdb_id=...,
    title=movie.title_fr if language == "fr" else movie.title_en,
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

## 🔒 User-Specific Filtering

In both flows, we always exclude:
- `seen` movies
- `watch later`
- `not interested`

These are tracked in the `UserMovie` table.

---

## 🌍 Multilingual Support

- All fields (title, overview, trailer, genres) are stored in both EN and FR
- Output is localized based on the `language` argument

---

## 🌐 External APIs Used

| API                          | Purpose                         |
|------------------------------|----------------------------------|
| TMDB `/discover/movie`       | Get movies by filters           |
| TMDB `/search/movie`         | Get TMDB ID from movie name     |
| TMDB `/movie/{id}`           | Get metadata + IMDb ID          |
| TMDB `/movie/{id}/videos`    | Get trailers                    |
| OMDB `?i=imdb_id`            | Get IMDb rating and vote count  |
| OpenAI Chat Completion       | Get similar movie titles        |

---

## ✅ Summary

Your movie pipeline supports:

- 🎯 Precise filter-based recommendations  
- 🤖 LLM-based similar movie discovery  
- 🧠 Smart multilingual enrichment  
- 💾 Efficient caching and refresh strategy  
- 👤 Per-user memory (seen, later, hidden)

Ready for high-performance, personalized movie discovery.

---
