# 🏗️ Architecture — MoviesYouDidntWatch.com

This document describes the backend architecture of **MoviesYouDidntWatch.com** — a modern, AI-powered movie recommender system that avoids redundant suggestions and helps users discover high-quality films through filters or natural language chat.

---

## 📐 System Overview

```
[ Client UI (React + Chat) ]
         │
         ▼
[ FastAPI Backend Layer ]
         │
 ┌───────┼────────┐
 ▼       ▼        ▼
API   Services   Database
         │
         ▼
External APIs (TMDB, OMDB, OpenAI)
```

---

## 🧱 Project Structure

```bash
app/backend/
├── api/            # FastAPI route definitions (REST)
├── core/           # Config, DB, clients, auth
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic request/response types
├── services/       # Business logic and recommendation engine
├── scripts/        # One-off scripts (e.g. genre mapping, DB init)
├── utils/          # Utility functions
└── main.py         # Application entrypoint
```

---

## 🧩 Core Components

### 1. 🔌 API Layer (`api/`)

Defines all public HTTP endpoints exposed to the frontend:

- `POST /auth/signup` / `login`
- `GET /users/me` + stats
- `POST /movies/search` (manual filtering)
- `POST /chat` (natural language interaction)
- `POST /me/movies/update_status` (seen/later/hidden)
- `GET /users/me/movies/*` (movie lists)

Routes are thin and delegate logic to corresponding services.

---

### 2. 🧠 Service Layer (`services/`)

Handles domain logic, data flow, and integration orchestration.

- `auth_service.py`: User registration, login, token issuance
- `movie_service.py`: Main pipeline for movie recommendations
- `llm_service.py`: Interacts with OpenAI to extract filters or suggest similar movies
- `session_service.py`: Manages assistant conversation context
- `user_movie_service.py`: Handles per-user movie actions
- `parser_service.py`: Extracts filters/intent from LLM replies

Multithreaded enrichment and per-user filtering are handled here.

---

### 3. 🗃️ Database Models (`models/`)

Defined using SQLAlchemy:

- `User`: Authentication and identity
- `CachedMovie`: Movie records enriched with TMDB + OMDB metadata
- `UserMovie`: Status of each movie for a user (seen/later/hidden)
- `ChatSession`: LLM interaction history, stored as JSON

Tables are normalized, indexed, and multilingual-ready.

---

### 4. 📦 Enrichment & Caching

Every movie is enriched with:

- TMDB (EN/FR title, overview, trailer)
- OMDB (IMDb rating, votes)
- Genre names and language mapping

Caching logic:
- Movies are cached locally in the database
- Data is refreshed every 7 days using `cache_update_date`
- Enrichment is multithreaded for performance

---

### 5. 🌐 External APIs

| API                       | Purpose                             |
|---------------------------|--------------------------------------|
| TMDB `/discover/movie`    | Filter-based movie discovery         |
| TMDB `/movie/{id}`        | Metadata + IMDb ID                   |
| TMDB `/movie/{id}/videos` | Trailer links                        |
| TMDB `/search/movie`      | Resolve movie titles to TMDB ID      |
| OMDB API                  | IMDb rating and vote count           |
| OpenAI GPT                | Similar movie suggestions, filter extraction |

---

## 🎬 Recommendation Engine

### `recommend_movies()` — Filter-based Discovery

```text
User Filters → TMDB → Enrich + Cache → Rerank by IMDb → MovieCard[]
```

Steps:
1. Fetch TMDB candidates page-by-page
2. Filter out seen/later/not_interested movies
3. Enrich new movies using TMDB + OMDB
4. Rerank results using IMDb rating or votes
5. Return localized `MovieCard[]`

---

### `recommend_similar_movies()` — LLM-based Discovery

```text
Movie Name → GPT → Similar Titles → TMDB IDs → Enrich → Filter → MovieCard[]
```

Steps:
1. Send movie name to OpenAI (`chat/completions`)
2. Resolve titles to TMDB IDs
3. Exclude seen/later/not_interested
4. Enrich and cache movie metadata
5. Return `MovieCard[]`

---

## 🔒 Security Model

- User auth is based on **JWT Bearer tokens**
- Passwords are hashed with `bcrypt`
- All sensitive routes require valid tokens
- Status changes (`seen`, `later`, etc.) are scoped by `user_id`

---

## 🌍 Multilingual Support

All movies are stored with dual-language fields:

- `title_en`, `title_fr`
- `overview_en`, `overview_fr`
- `trailer_url_en`, `trailer_url_fr`
- `genre_names_en`, `genre_names_fr`

Backend respects the `Accept-Language` header (`en` or `fr`) in API requests.

---

## 📊 Personalization

User interactions drive personalization:

- `UserMovie` table tracks `seen`, `watch later`, `not interested`
- These are always excluded from future suggestions
- User stats (top genres, average rating, watch count) are generated from SQL aggregations
- Assistant memory (chat sessions) is persisted per user

---

## 🧠 Assistant Logic

The assistant can:

- Extract filters from natural queries
- Recommend movies similar to a given title
- Maintain context within chat sessions
- Reply in the selected language

All logic passes through OpenAI GPT with role-controlled prompts and structured response parsing.

---

## ⚙️ Technologies

| Layer       | Stack                            |
|-------------|----------------------------------|
| Backend     | FastAPI, SQLAlchemy, Uvicorn     |
| Database    | PostgreSQL / SQLite (dev)        |
| Auth        | JWT, OAuth2 Password Flow        |
| AI          | OpenAI ChatCompletion (GPT-3.5/4)|
| Data APIs   | TMDB, OMDB                       |
| Caching     | SQL DB with refresh-on-read      |
| Parallelism | ThreadPoolExecutor for enrichment|

---

## 🧪 Testing & CI/CD

- Unit tests with `pytest` (WIP)
- `tests/` directory scaffolded
- `Dockerfile` for backend containerization
- `.env` support for API keys and secrets
- GitHub Actions planned for CI/CD pipelines

---

## ✅ Summary

**MoviesYouDidntWatch.com** is a production-ready, modular system designed for personalized movie discovery. It combines classic filtering with AI, supports multilingual outputs, avoids duplicate suggestions, and performs intelligent caching — all wrapped in a clean, scalable backend architecture.


---

movie-recommender-chatbot/
├── app
│   └── backend
│       ├── api
│       │   ├── auth_routes.py
│       │   ├── chat_routes.py
│       │   ├── movie_routes.py
│       │   ├── router.py
│       │   └── user_routes.py
│       ├── core
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── dependancies.py
│       │   ├── omdb_client.py
│       │   ├── openai_client.py
│       │   ├── security.py
│       │   └── tmdb_client.py
│       ├── models
│       │   ├── chat_session_model.py
│       │   ├── movie_model.py
│       │   ├── user_model.py
│       │   └── user_movie_model.py
│       ├── schemas
│       │   ├── chat_schemas.py
│       │   ├── movie_schemas.py
│       │   ├── stats_schemas.py
│       │   └── user_schemas.py
│       ├── scripts
│       │   ├── download_genres.py
│       │   └── init_db.py
│       ├── services
│       │   ├── auth_service.py
│       │   ├── chat_service.py
│       │   ├── llm_service.py
│       │   ├── movie_service.py
│       │   ├── parser_service.py
│       │   ├── session_service.py
│       │   └── user_movie_service.py
│       ├── utils
│       │   └── utils.py
│       └── main.py
├── data
│   └── processed
│       └── genres_mapping.json
├── docs
│   ├── api.md
│   ├── architecture.md
│   ├── data-models.md
│   ├── features.md
│   ├── movie_flow.md
│   ├── progress-backend.md
│   ├── schemas.md
│   └── user-flow.md
├── storage
│   └── movies.db
├── tests
│   └── test_placeholder.py
├── movie_service_test.py
├── requirements.txt
├── requirements-dev.txt
├── .env                          # Environment variables: API keys, secrets
├── .gitignore                    # Ignore __pycache__, .env, node_modules, etc.
├── DevNotes.md                   # This file you're reading
├── Dockerfile                    # For containerizing the backend app
└── README.md                     # Project intro, how to run, screenshots
