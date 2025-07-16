# 🗃️ SQLAlchemy Data Models — MoviesYouDidntWatch.com

This document defines all database tables using SQLAlchemy ORM. These models reflect the actual data used in the backend and support all functionality from user accounts to movie tracking and chat history.

---

## 👤 User

Represents a registered user.

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    joined = Column(DateTime, default=datetime.utcnow)
```

---

## 🎬 Movie

Represents a movie cached from TMDB/OMDB. Each entry is enriched with multilingual data and IMDb metadata.

```python
class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    tmdb_id = Column(Integer, unique=True, index=True, nullable=False)
    imdb_id = Column(String, nullable=True)

    title_en = Column(String, nullable=True)
    title_fr = Column(String, nullable=True)

    overview_en = Column(Text, nullable=True)
    overview_fr = Column(Text, nullable=True)

    poster_url = Column(String, nullable=True)
    trailer_en = Column(String, nullable=True)
    trailer_fr = Column(String, nullable=True)

    imdb_rating = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)

    genres = Column(ARRAY(String))         # e.g. ["Thriller", "Sci-Fi"]
    genre_ids = Column(ARRAY(Integer))     # TMDB genre IDs

    release_year = Column(Integer, nullable=True)
    original_language = Column(String, nullable=True)

    cached_on = Column(DateTime, default=datetime.utcnow)
    imdb_updated_on = Column(DateTime, default=datetime.utcnow)
```

---

## 🎯 UserMovie

Represents the relationship between a user and a movie (e.g. seen, watch later, not interested).

```python
class UserMovie(Base):
    __tablename__ = "user_movies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"))

    status = Column(Enum("seen", "later", "not_interested", name="movie_status"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="uq_user_movie"),)
```

> You can also store status as `String` instead of `Enum` if you want simpler migrations.

---

## 💬 ChatSession

Stores a sequence of messages exchanged between the user and the assistant.

```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)  # UUID string
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    conversation = Column(JSON)  # List of { role: "user" | "assistant", content: "..." }

    created_on = Column(DateTime, default=datetime.utcnow)
```

---

## 🔁 Relationships (Optional SQLAlchemy additions)

In `User`:
```python
movies = relationship("UserMovie", backref="user", cascade="all, delete-orphan")
chats = relationship("ChatSession", backref="user", cascade="all, delete-orphan")
```

In `Movie`:
```python
user_statuses = relationship("UserMovie", backref="movie", cascade="all, delete-orphan")
```

---

## 🧠 Notes

- Movies are cached locally to reduce TMDB/OMDB calls.
- IMDb data is refreshed periodically via `imdb_updated_on`.
- UserMovie rows define user-specific state: seen, later, or not interested.
- All foreign keys use `ondelete="CASCADE"` for clean deletions.

---
