# 🎬 Movie Flow — `movie_service.py`

This document describes the three main recommendation/search flows in the backend:

- `recommend_movies_by_filters()` → manual filter-based discovery  
- `recommend_similar_movies()` → LLM-powered similarity-based discovery  
- `search_movies_by_keywords()` → LLM-powered movie search by free-text keywords

Each function returns high-quality, localized `MovieCard` entries by:

- Fetching or resolving TMDB IDs  
- Enriching metadata with TMDB + OMDB  
- Caching results in the database  
- (Optionally) filtering out seen/later/hidden  
- Returning clean results in EN or FR

---

## 🔧 Function 1: `recommend_movies_by_filters()`

Manual filtering flow

```python
def recommend_movies_by_filters(filters: MovieSearchFilters, user_id: int, database: Session, language: str) -> list[MovieCard]
```

### 📥 Inputs:
- `filters`: genre, IMDb rating, votes, year, etc.
- `user_id`: used to exclude already marked movies
- `database`: SQLAlchemy session
- `language`: `"en"` or `"fr"`

---

### 🔁 Step-by-Step:

#### 1. Fetch up to 60 unseen TMDB movie IDs

```python
tmdb_ids = fetch_unseen_tmdb_ids(filters, user_id, database)
```

- Calls TMDB’s `/discover/movie` page-by-page
- Keeps only:
  - Movies where `genre_id` is 1st or 2nd in `genre_ids`
  - Movies not marked as seen/later/not_interested by user

---

#### 2. Enrich and cache metadata

```python
enrich_and_cache_movies(tmdb_ids)
```

- Each movie:
  - Checks freshness (≤ 7 days)
  - If stale → refreshes IMDb stats
  - If missing → fetches:
    - EN/FR title, overview, trailer
    - IMDb rating + votes
    - Genre names

---

#### 3. Fetch enriched cache

```python
cached_movies = fetch_movies_from_cache(tmdb_ids, database)
```

---

#### 4. Rerank and filter by IMDb metadata

```python
reranked = rerank_and_imdb_filter_movies(cached_movies, filters)
```

---

#### 5. Convert to `MovieCard`

```python
return [to_movie_card(m, language) for m in reranked]
```

---

## 🧠 Function 2: `recommend_similar_movies()`

LLM-powered movie similarity discovery

```python
def recommend_similar_movies(movie_name: str, user_id: int, database: Session, language: str) -> list[MovieCard]
```

### 📥 Inputs:
- `movie_name`: the base reference movie
- `user_id`: for excluding seen/later/hidden
- `database`: SQLAlchemy session
- `language`: `"en"` or `"fr"`

---

### 🔁 Step-by-Step:

#### 1. Ask OpenAI for similar titles

```python
similar_movies = ask_llm_for_similar_movies(movie_name)
```

Returns:

```python
[{"title": "Enemy", "year": 2013}, {"title": "The Lobster", "year": 2015}]
```

---

#### 2. Resolve to TMDB IDs

```python
tmdb_ids = [
    call_tmdb_movie_id_by_movie_name_endpoint(title, year)
    for title, year in similar_movies
]
```

---

#### 3. Filter out seen/later/hidden

```python
excluded_ids = fetch_excluded_ids(user_id, database)
filtered_ids = [id for id in tmdb_ids if id not in excluded_ids]
```

---

#### 4. Enrich and cache

```python
enrich_and_cache_movies(filtered_ids)
```

---

#### 5. Fetch and return `MovieCard` list

```python
cached_movies = fetch_movies_from_cache(filtered_ids, database)
return [to_movie_card(m, language) for m in cached_movies]
```

---

## 🔍 Function 3: `search_movies_by_title()`

LLM-powered keyword-based search

```python
def search_movies_by_title(title: str, database: Session, language: str) -> list[MovieCard]
```

### 📥 Inputs:
- `title`: free-form natural language query (e.g. "Ge tout", "Capten america")
- `database`: SQLAlchemy session
- `language`: `"en"` or `"fr"`

---

### 🔁 Step-by-Step:

#### 1. Ask OpenAI for matching movie titles

```python
matching_movies = ask_llm_for_matching_keywords_movies(keywords)
```

Returns:

```python
[{"title": "12 Angry Men", "year": 1957}, {"title": "Paths of Glory", "year": 1957}]
```

---

#### 2. Resolve to TMDB IDs

```python
tmdb_ids = [
    call_tmdb_movie_id_by_movie_name_endpoint(title, year)
    for title, year in matching_movies
]
```

---

#### 3. Enrich and cache results

```python
enrich_and_cache_movies(tmdb_ids)
```

---

#### 4. Fetch and return `MovieCard` list

```python
cached_movies = fetch_movies_from_cache(tmdb_ids, database)
return [to_movie_card(m, language) for m in cached_movies]
```

---

## 📦 Shared Enrichment Logic

All flows call:

```python
enrich_and_cache_movies(tmdb_ids)
```

Which uses:

```python
enrich_and_cache_one_movie(tmdb_id)
```

Each movie:
- Checks if already cached and fresh (≤ 7 days)
- Refreshes IMDb stats if stale
- If missing, fetches full metadata:
  - `title_*`, `overview_*`, `trailer_url_*`, `poster_url`
  - `imdb_rating`, `imdb_votes_count`
  - `genre_ids`, `genre_names_*`

---

## 🔒 User-Specific Filtering

Only `recommend_movies_by_filters()` and `recommend_similar_movies()` exclude:

- Seen movies
- Watch later
- Not interested

They are tracked in the `UserMedia` table.

---

## 🌍 Multilingual Support

All fields are stored in EN and FR.

```python
title = movie.title_fr if language == "fr" else movie.title_en
```

Applies to:
- `title`, `overview`, `trailer_url`, `genre_names`

---

## 🎬 `MovieCard` Output Model

All recommendation functions return:

```python
MovieCard(
    tmdb_id=...,
    imdb_id=...,
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

## 🌐 External APIs Used

| API                            | Purpose                         |
|--------------------------------|----------------------------------|
| TMDB `/discover/movie`         | Filter-based movie discovery     |
| TMDB `/search/movie`           | Resolve title → TMDB ID          |
| TMDB `/movie/{id}`             | Full movie metadata              |
| TMDB `/movie/{id}/videos`      | Trailer links                    |
| OMDB `?i=imdb_id`              | IMDb rating and vote count       |
| OpenAI Chat Completion         | Title suggestions + query match  |

---

## ✅ Summary

Your backend supports:

- 🎯 Precise filter-based movie discovery  
- 🤖 LLM-powered similarity and keyword-based search  
- 🔒 Personalized exclusion of seen/later/hidden  
- 🧠 Full multilingual support  
- 💾 Cached movie enrichment with weekly refresh  
- 🏎️ Parallelized data fetching for speed

---
