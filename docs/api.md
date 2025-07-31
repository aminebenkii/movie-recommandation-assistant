# 🧩 API Reference — MoviesYouDidntWatch.com

This document defines all public REST API endpoints used by the frontend, including authentication, user profile, movie & TV discovery, chat interaction, and user-specific media lists.

---

## 📑 Table of Contents

### 🔐 Authentication
- `POST /auth/signup`
- `POST /auth/login`

### 👤 User Profile
- `GET /users/me`

### 🎬 Movie Discovery
- `POST /movies/search-by-filters`
- `POST /movies/search-by-keywords`

### 📺 TV Show Discovery
- `POST /tvshows/search-by-filters`
- `POST /tvshows/search-by-keywords`

### 💬 Chat Assistant
- `POST /chat`

### ✅ Movie Status Actions
- `POST /me/movies/update_status`

### ✅ TV Show Status Actions
- `POST /me/tvshows/update_status`

### 📁 User Movie Lists
- `GET /me/movies/seen`
- `GET /me/movies/towatchlater`
- `GET /me/movies/hidden`

### 📁 User TV Show Lists
- `GET /me/tvshows/seen`
- `GET /me/tvshows/towatchlater`
- `GET /me/tvshows/hidden`

### 📊 User Stats
- `GET /users/me/stats`

---

## 🔐 Authentication

### `POST /auth/signup`

Registers a new user and returns an access token.

**Request Body:**
```json
{
  "first_name": "Amine",
  "last_name": "Benkirane",
  "email": "amine@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "<JWT>",
  "user": {
    "first_name": "Amine",
    "last_name": "Benkirane",
    "email": "amine@example.com"
  }
}
```

---

### `POST /auth/login`

Authenticates a user and returns a JWT token.

**Request Body:**
```json
{
  "email": "amine@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "<JWT>",
  "user": {
    "first_name": "Amine",
    "last_name": "Benkirane",
    "email": "amine@example.com"
  }
}
```

---

## 👤 User Profile

### `GET /users/me`

Returns the authenticated user’s profile.

**Headers:**
```
Authorization: Bearer <JWT>
```

**Response:**
```json
{
  "first_name": "Amine",
  "last_name": "Benkirane",
  "email": "amine@example.com"
}
```

---

## 🎬 Movie Discovery

### `POST /movies/search-by-filters`

Returns movies based on filter options like genre, rating, votes, release year, and language.

**Headers:**
```
Authorization: Bearer <JWT>
Accept-Language: en
```

**Request Body:**
```json
{
  "genre_name": "thriller",
  "min_imdb_rating": 7.0,
  "min_imdb_votes_count": 5000,
  "min_release_year": 1990,
  "max_release_year": 2023,
  "original_language": "en",
  "sort_by": "popularity.desc"
}
```

**Response:**
```json
[
  {
    "tmdb_id": 12345,
    "imdb_id": "tt8798780",
    "title": "Prisoners",
    "genre_names": ["Thriller", "Crime"],
    "release_year": 2013,
    "imdb_rating": 8.1,
    "imdb_votes_count": 75000,
    "poster_url": "...",
    "trailer_url": "...",
    "overview": "A father faces a moral dilemma after his daughter is kidnapped."
  }
]
```

---

### `POST /movies/search-by-title`

Returns movies based on a free-text natural language keyword search.

**Request Body:**
```json
{
  "keywords": "captain america"
}
```

**Response:**
```json
[
  {
    "tmdb_id": 54321,
    "imdb_id": "tt8798780",
    "title": "Captain America : the Return",
    "genre_names": ["Science Fiction", "Mystery"],
    "release_year": 2013,
    "imdb_rating": 7.2,
    "imdb_votes_count": 80000,
    "poster_url": "...",
    "trailer_url": "...",
    "overview": "A dinner party turns strange after a cosmic anomaly."
  }
]
```

---

## 📺 TV Show Discovery

### `POST /tvshows/search-by-filters`

Returns TV shows matching user-selected filters.

**Request Body:**
```json
{
  "genre_name": "thriller",
  "min_imdb_rating": 7.0,
  "min_imdb_votes_count": 5000,
  "min_release_year": 1990,
  "max_release_year": 2023,
  "original_language": "en",
  "sort_by": "popularity.desc"
}
```

**Response:**
```json
[
  {
    "tmdb_id": 67890,
    "imdb_id": "tt8798780",
    "title": "Squid Game",
    "genre_names": ["Drama", "Crime"],
    "release_year": 2017,
    "imdb_rating": 8.6,
    "imdb_votes_count": 160000,
    "poster_url": "...",
    "overview": "FBI agents interview serial killers to understand how they think."
  }
]
```

---

### `POST /tvshows/search-by-title`

Returns TV shows that match a free-form query.

**Request Body:**
```json
{
  "keywords": "chernobil"
}
```

**Response:**
```json
[
  {
    "tmdb_id": 321,
    "imdb_id": "tt8798780",
    "title": "Tchernobyl",
    "genre_names": ["Crime", "Drama", "Mystery"],
    "release_year": 2017,
    "imdb_rating": 7.9,
    "imdb_votes_count": 95000,
    "poster_url": "...",
    "overview": "A detective unravels the motive behind brutal acts."
  }
]
```

---

## 💬 Chat Assistant

### `POST /chat`

Processes a user’s natural language input and returns an assistant message + optional movie suggestions.

**Request Body:**
```json
{
  "session_id": "uuid-abc123",
  "query": "Find movies like Ex Machina or Her",
  "media_type": "movie/tvshow"
}
```

**Response:**
```json
{
  "message": "If you liked Ex Machina and Her, here are more AI-themed stories:",
  "results": [
    {
      "tmdb_id": 123,
      "imdb_id": "tt8798780",
      "title": "Upgrade",
      "genre_names": ["Sci-Fi", "Action"],
      "release_year": 2018,
      "imdb_rating": 7.5,
      "imdb_votes_count": 120000,
      "poster_url": "...",
      "overview": "A man is enhanced with AI to seek revenge."
    }
  ],
  "filters": {
    "genre_id": 878,
    "min_imdb_rating": 7.0,
    "original_language": "en",
    "sort_by": "vote_average.desc"
  }
}
```

---

## ✅ Movie Status Actions

### `POST /me/movies/update_status`

Marks a movie as `seen`, `towatchlater`, `hidden`, or resets status with `none`.

**Request Body:**
```json
{
  "tmdb_id": 12345,
  "status": "seen"
}
```

**Response:**
```json
{ "success": true }
```

---

## ✅ TV Show Status Actions

### `POST /me/tvshows/update_status`

Marks a TV show with a user-specific status.

**Request Body:**
```json
{
  "tmdb_id": 67890,
  "status": "towatchlater"
}
```

**Response:**
```json
{ "success": true }
```

---

## 📁 User Movie Lists

### `GET /me/movies/seen`  
### `GET /me/movies/towatchlater`  
### `GET /me/movies/hidden`

Returns the list of movies per status category.

**Response Format:**
```json
[
  {
    "tmdb_id": 123,
    "imdb_id": "tt8798780",
    "title": "Blade Runner 2049",
    "genre_names": ["Sci-Fi", "Drama"],
    "release_year": 2017,
    "imdb_rating": 8.0,
    "imdb_votes_count": 150000,
    "poster_url": "...",
    "overview": "A new blade runner discovers a secret that could destroy society."
  }
]
```

---

## 📁 User TV Show Lists

### `GET /me/tvshows/seen`  
### `GET /me/tvshows/towatchlater`  
### `GET /me/tvshows/hidden`

Returns the list of TV shows per status.

_Same response structure as above, using `TvShowCard` objects._

---

## 📊 User Stats

### `GET /users/me/stats`

Returns aggregate statistics about the user's viewing behavior.

**Response:**
```json
{
  "total_seen": 92,
  "top_genres": ["Drama", "Sci-Fi", "Thriller"],
  "average_rating_seen": 7.8,
  "most_watched_years": [2014, 2017, 2019],
  "average_release_year": 2011,
  "watch_later_count": 34
}
```

---

## 🧠 Notes

- All private routes require `Authorization: Bearer <JWT>`.
- Language support is handled via `Accept-Language: en` or `fr` headers.
- All movie/TV show data is localized and cached for speed.
- Chat assistant understands genre, rating, recency, and tone.
- Assistant can reference previous queries in a chat session.
- Similar movie and keyword routes use LLM + TMDB + OMDB.
- Duplicates (seen/later/hidden) are always excluded from recommendations.

---
