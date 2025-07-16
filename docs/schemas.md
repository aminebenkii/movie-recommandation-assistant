# 🧾 Pydantic Schemas — MoviesYouDidntWatch.com

These schemas validate request/response payloads across the API. They're grouped by domain: **users**, **movies**, **chat**, **user-movie actions**, and **stats**.

---

## 👤 User Schemas

### `UserCreate`
Used for signup (`POST /auth/signup`).
```python
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
```

---

### `UserLogin`
Used for login (`POST /auth/login`).
```python
class UserLogin(BaseModel):
    email: EmailStr
    password: str
```

---

### `UserPublic`
Returned after login or via `/users/me`.
```python
class UserPublic(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
```

---

### `TokenResponse`
Returned from `/auth/login` and `/auth/signup`.
```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
```

---

## 🎬 Movie Schemas

### `MovieCard`
Returned in most list-based responses.
```python
class MovieCard(BaseModel):
    tmdb_id: int
    title: str
    genres_names: list[str]
    release_year: int
    imdb_rating: float
    imdb_votes_count: int
    poster_url: str
    trailer_url: Optional[str] = None
    overview: Optional[str] = None
```

---

### `MovieSearchFilters`
Used in `/movies/search`.
```python
class MovieSearchFilters(BaseModel):
    genre_id: Optional[int] = None
    min_imdb_rating: Optional[float] = None
    min_imdb_votes_count: Optional[int] = None
    min_release_year: Optional[int] = None
    max_release_year: Optional[int] = None
    original_language: Optional[str] = "en"
    sort_by: Optional[Literal["popularity.desc", "vote_average.desc", "vote_count.desc"]] = "popularity.desc"
```

---


## 🎬 UserMovie Schemas

### `MovieStatusUpdate`
Used in `POST /user-movies`.
```python
class MovieStatusUpdate(BaseModel):
    tmdb_id: int
    status: Literal["seen", "later", "not_interested", "none"]
```

---

### `MovieListResponse`
Used in `/users/me/movies/*` routes and `/movies/search`.
```python
class MovieListResponse(BaseModel):
    movies: list[MovieCard]
```

---

## 💬 Chat Schemas

### `ChatQuery`
Used in `POST /chat`.
```python
class ChatQuery(BaseModel):
    session_id: str
    query: str
```

---

### `ChatResponse`
Returned by `POST /chat`.
```python
class ChatResponse(BaseModel):
    message: str
    movies: Optional[MovieListResponse] = None
    filters: Optional[MovieSearchFilters] = None
```

---

## 📊 Stats Schema

### `UserStats`
Returned by `GET /users/me/stats`.
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

## ✅ Utility Schemas

### `SuccessResponse`
Simple success indicator.
```python
class SuccessResponse(BaseModel):
    success: bool = True
```

---

### `Message`
Used for human-readable messages (errors, confirmations, etc).
```python
class Message(BaseModel):
    message: str
```

---


