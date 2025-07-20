# 🧾 Pydantic Schemas — MoviesYouDidntWatch.com

This document defines all **Pydantic schemas** used across the backend API for validating request and response payloads. Schemas are grouped by domain: **Users**, **Movies**, **Chat**, **User Movie Actions**, and **User Stats**.

---

## 📚 Table of Contents

- [👤 User Schemas](#-user-schemas)
  - [`UserCreate`](#usercreate)
  - [`UserLogin`](#userlogin)
  - [`UserPublic`](#userpublic)
  - [`TokenResponse`](#tokenresponse)
- [🎬 Movie Schemas](#-movie-schemas)
  - [`MovieCard`](#moviecard)
  - [`MovieSearchFilters`](#moviesearchfilters)
- [✅ UserMovie Schemas](#-usermovie-schemas)
  - [`MovieStatusUpdate`](#moviestatusupdate)
- [💬 Chat Schemas](#-chat-schemas)
  - [`ChatQuery`](#chatquery)
  - [`ChatResponse`](#chatresponse)
- [📊 Stats Schema](#-stats-schema)
  - [`UserStats`](#userstats)

---

## 👤 User Schemas

### `UserCreate`
Schema for user registration requests (`POST /auth/signup`).

```python
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
```

---

### `UserLogin`
Schema for user login requests (`POST /auth/login`).

```python
class UserLogin(BaseModel):
    email: EmailStr
    password: str
```

---

### `UserPublic`
Returned in user-related responses (e.g. `/users/me`, auth success).

```python
class UserPublic(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
```

---

### `TokenResponse`
Returned after successful signup or login.

```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
```

---

## 🎬 Movie Schemas

### `MovieCard`
Standard movie representation used across the API (e.g. search results, lists).

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

---

### `MovieSearchFilters`
Used to filter movie searches via manual filters or parsed chat intent.

```python
class MovieSearchFilters(BaseModel):
    genre_name: Optional[Literal[
        "action", "adventure", "animation", "comedy", "crime",
        "documentary", "drama", "family", "fantasy", "history",
        "horror", "music", "mystery", "romance", "science fiction",
        "tv movie", "thriller", "war", "western"
    ]] = None

    genre_id: Optional[int] = None
    min_imdb_rating: Optional[float] = None
    min_imdb_votes_count: Optional[int] = None
    min_release_year: Optional[int] = None
    max_release_year: Optional[int] = None
    original_language: Optional[str] = None
    sort_by: Optional[Literal[
        "popularity.desc",
        "vote_average.desc",
        "vote_count.desc"
    ]] = "popularity.desc"
```

---

## ✅ UserMovie Schemas

### `MovieStatusUpdate`
Used to set or update a movie status (seen, to-watch-later, hidden, or reset).

```python
class MovieStatusUpdate(BaseModel):
    tmdb_id: int
    status: Literal["seen", "towatchlater", "hidden", "none"]
```

---

## 💬 Chat Schemas

### `ChatQuery`
Schema for chat requests submitted by the user.

```python
class ChatQuery(BaseModel):
    session_id: str
    query: str
```

---

### `ChatResponse`
Returned after processing a user message via the AI assistant.

```python
class ChatResponse(BaseModel):
    message: str
    movies: Optional[list[MovieCard]]
    filters: Optional[MovieSearchFilters]
```

---

## 📊 Stats Schema

### `UserStats`
Provides high-level insights about the user's movie consumption.

```python
class UserStats(BaseModel):
    total_seen: int
    top_genres: list[str]
    average_rating_seen: float
    most_watched_years: list[int]
    average_release_year: int
    watch_later_count: int
```

---
