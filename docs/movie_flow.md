# 🎬 Movie Flow — `movie_service.py` Design

This document defines the full logic for fetching, filtering, enriching, and returning movie results from the TMDB + OMDB APIs — using caching, user-specific filtering, and reranking — before returning them as Pydantic `MovieCard`s.

---


## ✅ INPUT & OUTPUT MODELS

The recommendation pipeline receives a structured `MovieSearchFilters` object and returns a `MovieListResponse` containing at least 30 `MovieCard` entries.

---

### 🎯 INPUT — `MovieSearchFilters`

```python
class MovieSearchFilters(BaseModel):
    genre_name: Optional[Literal[
        "action", "adventure", "animation", "comedy", "crime", "documentary",
        "drama", "family", "fantasy", "history", "horror", "music", "mystery",
        "romance", "science fiction", "tv movie", "thriller", "war", "western"
    ]] = None                                           # → convert to genre_id internally
    genre_id: Optional[int] = None                      # → TMDB genre filter
    min_imdb_rating: Optional[float] = None             # → post-filtering or reranking
    min_imdb_votes_count: Optional[int] = None          # → post-filtering or reranking
    min_release_year: Optional[int] = None              # → TMDB primary_release_date.gte
    max_release_year: Optional[int] = None              # → TMDB primary_release_date.lte
    original_language: Optional[str] = None             # → TMDB with_original_language
    sort_by: Optional[Literal[
        "popularity.desc", 
        "vote_average.desc", 
        "vote_count.desc", 
        "release_date.desc"
    ]] = "popularity.desc"                              # → TMDB sort_by param
```

---

### 🧠 FUNCTION INTERFACE

```python
def recommend_movies(
    filters: MovieSearchFilters,
    user_id: int,
    db: Session,
    language: str
) -> list[MovieCard]
```

---

### 🎬 OUTPUT — `MovieCard` & `MovieListResponse`

```python
class MovieCard(BaseModel):
    tmdb_id: Optional[int]
    title: Optional[str]
    genre_names: Optional[list[str]]
    release_year: Optional[int] = None
    imdb_rating: Optional[float]
    imdb_votes_count: Optional[int]
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    overview: Optional[str] = None
```

```python
class MovieListResponse(BaseModel):
    movies: list[MovieCard]
```

The `recommend_movies()` pipeline should always return at least **30 filtered and enriched** `MovieCard` objects, suitable for frontend display — fully adapted to the selected language (`en` or `fr`).

---

## 🧱 Step-by-Step Flow

---

### 1. 🔍 Fetch from TMDB Discover API

We begin by calling TMDB's `/discover/movie` endpoint using the provided filters. The goal is to retrieve **2 pages** of movies (i.e. up to 40 candidates) in the selected `language`.

---

#### ✅ Required Query Parameters:

| Filter                | Purpose                                |
|------------------------|----------------------------------------|
| `language`             | Required, Ensures localized title, overview      |
| `page`                 | Required, Used to paginate (fetch multiple pages)|
| `with_genres`          | Optional, Filter by `genre_id`                   |
| `primary_release_date.gte` | Optional, Filter by release year (min)       |
| `primary_release_date.lte` | Optional, Filter by release year (max)       |
| `with_original_language`   | Optional language filter (e.g. `"en"`) |
| `sort_by`              | Optional, Sorting logic: `"popularity.desc"` (default), or `"vote_average.desc"`, etc.

Only movies with meaningful relevance are retained by **post-filtering on genre priority** (see below).

---


### ✅ Store all valid results in a list called `raw_movies`.

---

### 📦 Sample Response from TMDB Discover API:

```json
{
  "page": 1,
  "results": [
    {
      "adult": false,
      "backdrop_path": "/nKyBbFSooRPTJVqjrDteD1lF733.jpg",
      "genre_ids": [28, 12, 18],
      "id": 1011477,
      "original_language": "en",
      "original_title": "Karate Kid: Legends",
      "overview": "After a family tragedy, kung fu prodigy Li Fong is uprooted from his home in Beijing...",
      "popularity": 750.3586,
      "poster_path": "/AEgggzRr1vZCLY86MAp93li43z.jpg",
      "release_date": "2025-05-08",
      "title": "Karate Kid: Legends",
      "video": false,
      "vote_average": 7.3,
      "vote_count": 376
    }
  ],
  "total_pages": 500,
  "total_results": 10000
}
```

---

### 🧠 Notes:

- Fields like `title`, `overview`, `poster_path`, `release_date`, `genre_ids`, and `vote_average` are **immediately available**
- ❌ Trailers are **not included** — require separate call to `/movie/{id}/videos`
- ❌ IMDb ID is **not included** — must call `/movie/{id}/external_ids`
- ❌ Genre names are **not included** — use local `genres_mapping.json` to convert IDs → names

---


---

### 2. 🧹 Filter Unwanted Movies (Genre + User Status)

After fetching movies from TMDB, we apply two critical filtering steps to build a clean, relevant movie list before enrichment.

---

#### ⚠️ Critical Genre Filter Rule:

We **only keep** a movie if the requested `genre_id` appears as the **first or second** item in `genre_ids`.

This helps avoid edge-case results like:
> `"Drama, Thriller, Mystery, Comedy"`  
when the user clearly wants **comedy-first** movies.

---

#### 🟪 Step 1: Filter by Genre Priority

We **only keep** movies where the requested `genre_id` appears as the **first or second element** of the `genre_ids` list.

This prevents low-relevance results like:
> `"Drama, Thriller, Comedy"`  
when the user is clearly asking for **Comedy-first** recommendations.

```python
# Pseudocode:
if genre_id not in movie["genre_ids"][:2]:
    skip
```

---

#### 🟦 Step 2: Filter Out Seen or Skipped Movies

Next, we eliminate all movies the user has already interacted with:

- Movies marked as:
  - ✅ Seen
  - ⏱ Watch Later
  - ❌ Not Interested

These TMDB IDs are fetched once from the `UserMovie` table and stored in a set for efficient exclusion.

```python
excluded_tmdb_ids = {12345, 67890, ...}

filtered_movies = [
    movie for movie in raw_movies
    if movie["tmdb_id"] not in excluded_tmdb_ids
]
```

---

### 🔁 Repeat Pagination if Needed

If, after applying both filters, you have **fewer than 30 unique movies**, fetch the next page from TMDB and repeat both filters:

1. Check genre relevance
2. Check user status
3. Add to `raw_movies` only if passes both

Use a `set()` of collected TMDB IDs to avoid duplicates across pages.

```python
seen_tmdb_ids = set()
...
if movie["id"] in seen_tmdb_ids:
    continue
```

---

### ✅ Result

After this step, you now have:
- A deduplicated, high-relevance, genre-prioritized list of movie dicts
- None of which have been previously marked by the user
- Ready for enrichment (IMDb, trailer, caching)

Stored in:
```python
filtered_movies: list[dict]  # raw TMDB movies
```

---


---


### 3. 🧠 Enrich with IMDb Data, Trailers, and Multilingual Fields

At this stage, we have a filtered list of raw TMDB movie dicts (from the `/discover/movie` endpoint in either English or French).  
Now we enrich each movie with:

- 🎞 IMDb rating and vote count (from OMDB)  
- 🎬 Trailer URLs in both English and French  
- 🎭 Genre name strings (from local map)  
- 🌍 Multilingual fields: title, overview (both EN and FR)

We apply a **cache-first strategy**, and only hit external APIs if the movie is new or stale.

---

### ✅ Enrichment Steps for Each Movie

#### 🟢 A. Check for Fresh Cache

Query the database:

```sql
SELECT * FROM movies
WHERE tmdb_id = :id AND cache_update_date >= today - 7 days
```

If a fresh entry exists:
- ✅ Use directly:
  - `title_en` / `title_fr`
  - `overview_en` / `overview_fr`
  - `poster_url`
  - `release_year`
  - `imdb_rating`, `imdb_votes_count`
  - `genre_names_en`, `genre_names_fr`
  - `trailer_url_en`, `trailer_url_fr`

➡️ No API calls required — fully served from cache.

---

#### 🟡 B. If Cache is Stale (older than 7 days)

- ✅ Reuse everything in cache **except IMDb metadata**
- 🔄 Refresh only:
  - `imdb_rating` and `imdb_votes_count` via OMDB
- 🕒 Update `cache_update_date` to today

```python
movie.imdb_rating = updated_rating
movie.imdb_votes_count = updated_votes
movie.cache_update_date = date.today()
```

➡️ Only 1 OMDB call is made — no TMDB calls.

---

#### 🔴 C. If Movie Not in Cache

Fetch and cache all required fields:

1. **Step 1 — Discover Results (already available)**
   From the initial `/discover/movie?language=XX` call, you already have:
   - `title_en` or `title_fr` (depending on discovery language)
   - `overview_en` or `overview_fr`
   - `poster_path` → construct `poster_url`
   - `release_date` → extract `release_year`
   - `genre_ids`

2. **Step 2 — Get IMDb ID + Opposite Language Fields**
   Call:
   ```http
   GET /movie/{id}?language=FR or EN
   ```
   to get:
   - `imdb_id`
   - Missing `title_xx`, `overview_xx` (opposite language)

3. **Step 3 — Get Trailer URLs**
   - `GET /movie/{id}/videos?language=en-US` → `trailer_url_en`
   - `GET /movie/{id}/videos?language=fr-FR` → `trailer_url_fr`

4. **Step 4 — Get IMDb Metadata**
   - `GET OMDB ?i=imdb_id` → `imdb_rating`, `imdb_votes_count`

5. **Step 5 — Map Genre IDs to Names**
   Use your local `genres_mapping.json` to generate:
   - `genre_names_en`
   - `genre_names_fr`

6. **Step 6 — Cache the New Entry**
   Store all data in the `movies` table for future use.

---

### 📥 Final `Movie` SQLAlchemy Model

```python
class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True)
    imdb_id = Column(String, nullable=False, unique=True)

    imdb_rating = Column(Float, nullable=False)
    imdb_votes_count = Column(Integer, nullable=False)

    release_year = Column(Integer, nullable=False)
    poster_url = Column(String, nullable=False)

    title_en = Column(String, nullable=True)
    title_fr = Column(String, nullable=True)

    overview_en = Column(String, nullable=True)
    overview_fr = Column(String, nullable=True)

    genre_ids = Column(JSON, nullable=False)
    genre_names_en = Column(JSON, nullable=True)
    genre_names_fr = Column(JSON, nullable=True)

    trailer_url_en = Column(String, nullable=True)
    trailer_url_fr = Column(String, nullable=True)

    cache_update_date = Column(Date, nullable=False, default=date.today)
```

---

### 🧠 Notes

- All enrichment and caching happens **before reranking or MovieCard conversion**
- Cached entries are refreshed lazily every 7 days
- API calls are **parallelizable** per movie for speed
- After caching, the movie is fully ready to serve UI or search

---


### 4. 🧠 Reranking Logic (Based on IMDb Metadata)

By this stage, we have a list of 30+ enriched movies, originally ordered by TMDB’s `sort_by` parameter. Depending on the chosen sort strategy, we may apply **additional reranking using IMDb metadata**.

---

### 🧩 User-Supplied `sort_by` Options

Users can choose one of the following sort options:

| sort_by              | TMDB Behavior                     | Our Backend Behavior              |
|----------------------|-----------------------------------|-----------------------------------|
| `popularity.desc`    | Sorts by TMDB popularity signal   | ✅ No reranking                   |
| `vote_average.desc`  | Sorts by TMDB vote_average        | ✅ Rerank using IMDb rating       |
| `vote_count.desc`    | Sorts by TMDB vote_count          | ✅ Rerank using IMDb vote count   |

---

### 🧠 Why?

- **TMDB vote_average** and **vote_count** are often inflated or regional.
- IMDb ratings and vote counts are generally more trustworthy.
- We want to respect the user's intent — but use **IMDb as our quality filter**.

---

### ✅ Backend Reranking Rules

```python
if sort_by == "vote_average.desc":
    movies.sort(key=lambda m: m["imdb_rating"], reverse=True)

elif sort_by == "vote_count.desc":
    movies.sort(key=lambda m: m["imdb_votes_count"], reverse=True)

elif sort_by == "popularity.desc":
    # No reranking needed — already sorted by TMDB
    pass
```

---

### 📌 Notes

- Reranking is applied **after** all filtering and enrichment is complete
- All IMDb fields are guaranteed present by this stage (due to enrichment logic)
- This system allows **high-quality control** without complicating the user-facing API

---

After this step, we now have the final list of **clean, filtered, enriched, and sorted** movie dicts — ready for conversion into `MovieCard` models.

---


## 🎨 Final Step: Convert to `MovieCard`

For each enriched movie:
```python
MovieCard(
    tmdb_id=movie.tmdb_id,
    title=movie.title_fr if language == "fr" else movie.title_en,
    genre_names=movie.genre_names_fr if language == "fr" else movie.genre_names_en,
    release_year=movie.release_year,
    imdb_rating=movie.imdb_rating,
    imdb_votes_count=movie.imdb_votes_count,
    poster_url=movie.poster_url,
    trailer_url=movie.trailer_url_fr if language == "fr" else movie.trailer_url_en,
    overview=movie.overview_fr if language == "fr" else movie.overview_en,
)
```

---

## ✅ Summary of External API Usage

| API Endpoint                              | Purpose                                   | Example Helper Function            |
|-------------------------------------------|-------------------------------------------|------------------------------------|
| `TMDB /discover/movie`                    | Initial list of candidate movies          | — (called in `fetch_tmdb_discover`) |
| `TMDB /movie/{id}`                        | Get IMDb ID (`imdb_id`) for a TMDB movie  | `get_imdb_id_from_tmdb()`         |
| `TMDB /movie/{id}/videos`                 | Get trailer link (YouTube if possible)    | `get_trailers()`                  |
| `OMDB ?i={imdb_id}&apikey=...`            | Get IMDb rating and vote count            | `get_imdb_details()`              |

---

### ✅ Examples of Call Results

- **`get_imdb_id_from_tmdb(id)`** → `"tt0133093"`  
- **`get_trailers(id)`** → `"https://www.youtube.com/watch?v=abc123"`  
- **`get_imdb_details(imdb_id)`** → `{"imdb_rating": "8.7", "imdb_votes": "1,900,000"}`

---

These functions are used only when a movie is **not in cache** or when the **cache is stale**. The responses are normalized and inserted into the DB as part of the enrichment step.

---



---

## 🧠 Final Pipeline Overview — `recommend_movies()` Main Flow

The main function orchestrates the entire recommendation process, using a series of focused helper subfunctions.

---

### 🔧 Function Signature

```python
def recommend_movies(
    filters: MovieSearchFilters,
    user_id: int,
    db: Session,
    language: str
) -> list[MovieCard]
```

---

### 🧭 Main Flow

```python
def recommend_movies(filters, user_id, db, language):
    
    # 1. Fetch initial candidate movies from TMDB
    raw_movies = fetch_tmdb_discover(filters, language)
    
    # 2. Filter out low-priority genres and previously seen/listed movies
    filtered_movies = filter_relevant_movies(raw_movies, filters.genre_id, user_id, db)

    # 3. Ensure we have at least 30 valid movies (with deduping and pagination)
    while len(filtered_movies) < 30:
        more_movies = fetch_next_page(...)
        filtered_more = filter_relevant_movies(more_movies, filters.genre_id, user_id, db)
        filtered_movies.extend(filtered_more)
        # dedupe by tmdb_id

    # 4. Enrich each movie using cache or API calls
    enriched_movies = enrich_with_imdb_and_trailer(filtered_movies, db, language)

    # 5. Optionally rerank results based on selected sort_by
    ranked_movies = rerank_movies(enriched_movies, filters.sort_by)

    # 6. Transform into Pydantic models
    return [to_movie_card(movie, language) for movie in ranked_movies]
```

---

## 🧩 Subfunction Responsibilities

### `fetch_tmdb_discover(filters, language) → list[dict]`
Calls TMDB Discover API with filters and returns movie result dicts from 1 or more pages.

---

### `filter_relevant_movies(movies, genre_id, user_id, db) → list[dict]`
- Filters by genre priority (genre_id must be 1st or 2nd in genre_ids)
- Removes `seen`, `watch_later`, and `not_interested` movies for the user

---

### `enrich_with_imdb_and_trailer(movies, db, language) → list[dict]`
- Uses cache if fresh
- Otherwise, calls TMDB (`external_ids`, `videos`) and OMDB
- Updates or inserts into cache
- Adds:
  - `imdb_rating`, `imdb_votes_count`
  - `genre_names_{lang}`
  - `trailer_url_{lang}`

---

### `rerank_movies(movies, sort_by) → list[dict]`
- Only applied if `sort_by` is `"vote_average.desc"` or `"vote_count.desc"`
- Uses IMDb data for true ranking

---

### `to_movie_card(movie_dict, language) → MovieCard`
- Converts an enriched dict (from DB or TMDB/OMDB) into a `MovieCard` Pydantic model
- Uses `title`, `overview`, `genre_names`, `trailer_url` in correct language

---

### ✅ Output
Final result is returned as:
```python
List[MovieCard]
```

---
