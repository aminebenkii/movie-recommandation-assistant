# 📺 TV Show Flow — `tvshow_service.py`

This document describes the three main recommendation/search flows in the backend:

- `recommend_tvshows_by_filters()` → manual filter-based discovery  
- `recommend_similar_tvshows()` → LLM-powered similarity-based discovery  
- `search_tvshows_by_keywords()` → LLM-powered TV show search by free-text keywords

Each function returns high-quality, localized `TVShowCard` entries by:

- Fetching or resolving TMDB IDs  
- Enriching metadata with TMDB + OMDB  
- Caching results in the database  
- (Optionally) filtering out seen/later/hidden  
- Returning clean results in EN or FR

---

## 🔧 Function 1: `recommend_tvshows_by_filters()`

Manual filtering flow

```python
def recommend_tvshows_by_filters(filters: TVShowSearchFilters, user_id: int, database: Session, language: str) -> list[TVShowCard]
```

### 📥 Inputs:
- `filters`: genre, IMDb rating, votes, year, etc.
- `user_id`: used to exclude already marked TV shows
- `database`: SQLAlchemy session
- `language`: `"en"` or `"fr"`

---

### 🔁 Step-by-Step:

#### 1. Fetch up to 60 unseen TMDB TV show IDs

```python
tmdb_ids = fetch_unseen_tmdb_ids(filters, user_id, database)
```

- Calls TMDB’s `/discover/tv` page-by-page
- Keeps only:
  - TV shows where `genre_id` is 1st or 2nd in `genre_ids`
  - TV shows not marked as seen/later/not_interested by user

---

#### 2. Enrich and cache metadata

```python
enrich_and_cache_tvshows(tmdb_ids)
```

- Each TV show:
  - Checks freshness (≤ 7 days)
  - If stale → refreshes IMDb stats
  - If missing → fetches:
    - EN/FR name, overview, trailer
    - IMDb rating + votes
    - Genre names

---

#### 3. Fetch enriched cache

```python
cached_tvshows = fetch_tvshows_from_cache(tmdb_ids, database)
```

---

#### 4. Rerank and filter by IMDb metadata

```python
reranked = rerank_and_imdb_filter_tvshows(cached_tvshows, filters)
```

---

#### 5. Convert to `TVShowCard`

```python
return [to_tvshow_card(tv, language) for tv in reranked]
```

---

## 🧠 Function 2: `recommend_similar_tvshows()`

LLM-powered TV show similarity discovery

```python
def recommend_similar_tvshows(tvshow_name: str, user_id: int, database: Session, language: str) -> list[TVShowCard]
```

### 📥 Inputs:
- `tvshow_name`: the base reference TV show
- `user_id`: for excluding seen/later/hidden
- `database`: SQLAlchemy session
- `language`: `"en"` or `"fr"`

---

### 🔁 Step-by-Step:

#### 1. Ask OpenAI for similar titles

```python
similar_tvshows = ask_llm_for_similar_tvshows(tvshow_name)
```

Returns:

```python
[{"title": "Dark", "year": 2017}, {"title": "The OA", "year": 2016}]
```

---

#### 2. Resolve to TMDB IDs

```python
tmdb_ids = [
    call_tmdb_tv_id_by_tvshow_name_endpoint(title, year)
    for title, year in similar_tvshows
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
enrich_and_cache_tvshows(filtered_ids)
```

---

#### 5. Fetch and return `TVShowCard` list

```python
cached_tvshows = fetch_tvshows_from_cache(filtered_ids, database)
return [to_tvshow_card(tv, language) for tv in cached_tvshows]
```

---

## 🔍 Function 3: `search_tvshows_by_title()`

LLM-powered keyword-based search

```python
def search_tvshows_by_title(title: str, database: Session, language: str) -> list[TVShowCard]
```

### 📥 Inputs:
- `title`: free-form natural language query (e.g. "gim of trons", "brekin bad")
- `database`: SQLAlchemy session
- `language`: `"en"` or `"fr"`

---

### 🔁 Step-by-Step:

#### 1. Ask OpenAI for matching TV show titles

```python
matching_tvshows = ask_llm_for_matching_keywords_tvshows(keywords)
```

Returns:

```python
[{"title": "Breaking Bad", "year": 2008}, {"title": "Better Call Saul", "year": 2015}]
```

---

#### 2. Resolve to TMDB IDs

```python
tmdb_ids = [
    call_tmdb_tv_id_by_tvshow_name_endpoint(title, year)
    for title, year in matching_tvshows
]
```

---

#### 3. Enrich and cache results

```python
enrich_and_cache_tvshows(tmdb_ids)
```

---

#### 4. Fetch and return `TVShowCard` list

```python
cached_tvshows = fetch_tvshows_from_cache(tmdb_ids, database)
return [to_tvshow_card(tv, language) for tv in cached_tvshows]
```

---

## 📦 Shared Enrichment Logic

All flows call:

```python
enrich_and_cache_tvshows(tmdb_ids)
```

Which uses:

```python
enrich_and_cache_one_tvshow(tmdb_id)
```

Each TV show:
- Checks if already cached and fresh (≤ 7 days)
- Refreshes IMDb stats if stale
- If missing, fetches full metadata:
  - `name_*`, `overview_*`, `trailer_url_*`, `poster_url`
  - `imdb_rating`, `imdb_votes_count`
  - `genre_ids`, `genre_names_*`

---

## 🔒 User-Specific Filtering

Only `recommend_tvshows_by_filters()` and `recommend_similar_tvshows()` exclude:

- Seen TV shows  
- Watch later  
- Not interested  

They are tracked in the `UserMedia` table.

---

## 🌍 Multilingual Support

All fields are stored in EN and FR.

```python
title = tvshow.name_fr if language == "fr" else tvshow.name_en
```

Applies to:
- `name`, `overview`, `trailer_url`, `genre_names`

---

## 📺 `TVShowCard` Output Model

All recommendation functions return:

```python
TVShowCard(
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

| API                            | Purpose                           |
|--------------------------------|------------------------------------|
| TMDB `/discover/tv`            | Filter-based TV show discovery     |
| TMDB `/search/tv`              | Resolve title → TMDB ID            |
| TMDB `/tv/{id}`                | Full TV show metadata              |
| TMDB `/tv/{id}/videos`         | Trailer links                      |
| OMDB `?i=imdb_id`              | IMDb rating and vote count         |
| OpenAI Chat Completion         | Title suggestions + query match    |

---

## ✅ Summary

Your backend supports:

- 🎯 Precise filter-based TV show discovery  
- 🤖 LLM-powered similarity and keyword-based search  
- 🔒 Personalized exclusion of seen/later/hidden  
- 🧠 Full multilingual support  
- 💾 Cached TV show enrichment with weekly refresh  
- 🏎️ Parallelized data fetching for speed


"Each Markdown section should be in a raw code block (use ```markdown inside and wrap the whole reply with ``` to prevent rendering)."