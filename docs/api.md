# 🧩 API Reference — MoviesYouDidntWatch.com

This file defines all public REST endpoints used by the frontend — including authentication, user profile, movie discovery, chat interaction, and personalized movie lists.

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

Logs in an existing user.

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

## 👤 User

### `GET /users/me`

Returns the currently authenticated user.

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

Returns filtered movie results based on manual filters.

**Request Body:**
```json
{
  "genre_id": 35,
  "min_rating": 7.0,
  "min_votes": 5000,
  "start_year": 1990,
  "end_year": 2023,
  "language": "en",
  "sort_by": "popularity.desc"
}
```

**Response:**
```json
[
  {
    "tmdb_id": 12345,
    "title": "The Nice Guys",
    "poster": "...",
    "rating": 7.4,
    "vote_count": 95000,
    "genres": ["Comedy", "Action"],
    "release_year": 2016
  }
]
```

> Applies backend filtering and paginates until at least 25 valid movies are found.

---

## 💬 Chat Assistant

### `POST /chat`

Processes a user’s natural language input and returns assistant response and matching movies.

**Request Body:**
```json
{
  "session_id": "uuid-abc123",
  "query": "Show me underrated sci-fi from the 90s"
}
```

**Response:**
```json
{
  "message": "Here are some lesser-known sci-fi gems from the 1990s 👇",
  "movies": [
    {
      "id": 603,
      "title": "The Matrix",
      "year": 1999,
      "imdb_rating": 8.7,
      "vote_count": 1900000,
      "genres": ["Action", "Sci-Fi"],
      "poster_url": "...",
      "tmdb_id": 603
    }
  ],
  "filters": {
    "genre": "Science Fiction",
    "year_range": [1990, 1999],
    "sort_by": "imdb_rating",
    "min_votes": 1000
  }
}
```

> The assistant understands genre, tone, year, rating, and even suggests from currently visible movie list if prompted.

---

## ✅ User Movie Actions

### `POST /user-movies`

Sets or updates the relationship between the current user and a movie.

**Request Body:**
```json
{
  "tmdb_id": 12345,
  "status": "seen"  // or "later", "not_interested", "none"
}
```

- `"none"` removes the movie from all lists.
- Replaces any previous status.

**Response:**
```json
{ "success": true }
```

---

## 📁 User-Specific Movie Lists

### `GET /users/me/movies/seen`

Returns movies marked as “Seen”.

**Headers:**
```
Authorization: Bearer <JWT>
```

**Response:**
```json
[
  {
    "tmdb_id": 12345,
    "title": "The Nice Guys",
    "poster": "...",
    "rating": 7.4,
    "vote_count": 95000,
    "genres": ["Comedy", "Action"],
    "release_year": 2016,
    "trailer_url": "https://youtube.com/..."
  }
]
```

---

### `GET /users/me/movies/later`

Returns movies saved for “Watch Later”.

_Same format as `/movies/seen`._

---

### `GET /users/me/movies/not-interested`

Returns rejected movies marked as “Not Interested”.

_Same format as `/movies/seen`._

---

## 📊 User Stats

### `GET /users/me/stats`

Returns aggregated viewing statistics.

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

> Note: MVP uses simple SQL. More advanced insights can come later.

---

## 🧠 Notes

- All authenticated routes require `Authorization: Bearer <JWT>`
- Movie actions and lists are user-specific
- Chat and manual filters are synchronized internally
- All movie data is cached on first fetch, then reused
- Assistant is context-aware (can reference movies currently on screen)

---

