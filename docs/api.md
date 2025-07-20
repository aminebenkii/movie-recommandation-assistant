# 🧩 API Reference — MoviesYouDidntWatch.com

This file defines all public REST API endpoints used by the frontend, including authentication, user profile, movie discovery, chat interaction, and user-specific movie lists.

---

## 📑 Table of Contents

- 🔐 `POST /auth/signup`
- 🔐 `POST /auth/login`
- 👤 `GET /users/me`
- 🎬 `POST /movies/search`
- 💬 `POST /chat`
- ✅ `POST /me/movies/update_status`
- 📁 `GET /users/me/movies/seen`
- 📁 `GET /users/me/movies/towatchlater`
- 📁 `GET /users/me/movies/hidden`
- 📊 `GET /users/me/stats`

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

Logs in an existing user and returns an access token.

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

Returns the currently authenticated user's profile.

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

### `POST /movies/search`

Returns movies based on manual filters like genre, IMDb rating, release year, etc.

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
    "title": "The Nice Guys",
    "genre_names": ["Comedy", "Drama"],
    "release_year": 2016,
    "imdb_rating": 7.4,
    "imdb_votes_count": 95000,
    "poster_url": "https://...",
    "trailer_url": "https://...",
    "overview": "A private investigator and a tough enforcer team up in 1970s Los Angeles..."
  }
]
```

> Returns a list of movies matching the given filters. Backend paginates TMDB results until at least 30 valid movies are found.

---

## 💬 Chat Assistant

### `POST /chat`

Processes a user’s natural language query and returns an assistant response, along with optional movie recommendations and extracted filters.

**Headers:**
```
Authorization: Bearer <JWT>
Accept-Language: en
```

**Request Body:**
```json
{
  "session_id": "uuid-abc123",
  "query": "Show me underrated sci-fi movies from the 90s"
}
```

**Response:**
```json
{
  "message": "Here are some lesser-known sci-fi gems from the 1990s 👇",
  "movies": [
    {
      "tmdb_id": 12345,
      "title": "Dark City",
      "genre_names": ["Science Fiction", "Mystery"],
      "release_year": 1998,
      "imdb_rating": 7.6,
      "imdb_votes_count": 120000,
      "poster_url": "https://...",
      "trailer_url": "https://...",
      "overview": "A man struggles with memories of his past in a dystopian city ruled by shadows."
    }
  ],
  "filters": {
    "genre_name": "science fiction",
    "min_imdb_rating": 7.0,
    "min_imdb_votes_count": 1000,
    "min_release_year": 1990,
    "max_release_year": 1999,
    "original_language": "en",
    "sort_by": "vote_average.desc"
  }
}
```

**Behavior:**

- Saves the query to the user's current chat session.
- Sends the conversation to the LLM assistant.
- Parses assistant output for:
  - `filters` → structured movie filters
  - `similar_movie` → reference movie name
- Returns a cleaned assistant message, relevant movie results (if any), and extracted filters.

> The assistant understands tone, genres, date ranges, IMDb filters, and can contextually respond based on your conversation.

---

## ✅ Movie Status Actions

### `POST /me/movies/update_status`

Updates the current user's relationship to a movie.

**Headers:**
```
Authorization: Bearer <JWT>
```

**Request Body:**
```json
{
  "tmdb_id": 12345,
  "status": "seen"  // or "towatchlater", "hidden", "none"
}
```

- `"none"` removes the movie from all lists.
- Replaces any existing status.

**Response:**
```json
{ "success": true }
```

---

## 📁 User Movie Lists

### `GET /users/me/movies/seen`

Returns all movies marked as **Seen** by the user.

**Headers:**
```
Authorization: Bearer <JWT>
Accept-Language: en
```

**Response:**
```json
[
  {
    "tmdb_id": 12345,
    "title": "The Nice Guys",
    "genre_names": ["Comedy", "Drama"],
    "release_year": 2016,
    "imdb_rating": 7.4,
    "imdb_votes_count": 95000,
    "poster_url": "...",
    "trailer_url": "...",
    "overview": "..."
  }
]
```

---

### `GET /users/me/movies/towatchlater`

Returns all movies saved in the **Watch Later** list.

_Same format as above._

---

### `GET /users/me/movies/hidden`

Returns all movies marked as **Not Interested**.

_Same format as above._

---

## 📊 User Stats

### `GET /users/me/stats`

Returns aggregated statistics about the user's viewing activity.

**Headers:**
```
Authorization: Bearer <JWT>
```

**Response:**
```json
{
  "total_seen": 78,
  "top_genres": ["Thriller", "Drama", "Sci-Fi"],
  "average_rating_seen": 7.6,
  "most_watched_years": [2014, 2019],
  "average_release_year": 2011,
  "watch_later_count": 21
}
```

> Stats are calculated using basic SQL aggregation. Advanced insights can be added later.

---

## 🧠 Notes

- All authenticated routes require the `Authorization: Bearer <JWT>` header.
- Movie suggestions are always filtered based on the user's existing "Seen", "Watch Later", and "Not Interested" lists.
- Chat and manual filters are internally unified under the same recommendation logic.
- TMDB and OMDB data is cached after first fetch for better performance.
- Chat assistant maintains context during a session and can reference prior interactions.

---
