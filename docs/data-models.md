# 🗃️ SQLAlchemy Data Models — MoviesYouDidntWatch.com

This document defines the full database schema using **SQLAlchemy ORM**. These models represent core backend entities: user accounts, cached movies, user-specific movie interactions, and AI chat session history. All fields are designed to support multilingual content, efficient lookups, and clean relational integrity.

---

## 📑 Table of Contents

1. [👤 User](#-user)
2. [🎬 CachedMovie](#-cachedmovie)
3. [🎯 UserMovie](#-usermovie)
4. [💬 ChatSession](#-chatsession)
5. [🔁 Relationships (Optional)](#-relationships-optional)
6. [🧠 Design Notes](#-design-notes)

---

## 👤 User

Represents a registered user of the platform.

```python
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.backend.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    joined = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User(id = {self.id}, name = {self.first_name} {self.last_name}, email = {self.email}, joined on : {self.joined})>"
```

---

## 🎬 CachedMovie

Represents a movie cached from TMDB and enriched with multilingual and IMDb metadata.

```python
from sqlalchemy import Column, String, Integer, Float, Date, JSON
from datetime import date
from app.backend.core.database import Base

class CachedMovie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, index=True, unique=True)
    imdb_id = Column(String, nullable=False, unique=True)

    imdb_rating = Column(Float, nullable=False)
    imdb_votes_count = Column(Integer, nullable=False)

    release_year = Column(Integer, nullable=False)
    poster_url = Column(String, nullable=False)

    title_en = Column(String, nullable=True)
    title_fr = Column(String, nullable=True)

    genre_ids = Column(JSON, nullable=False)

    genre_names_en = Column(JSON, nullable=True)
    genre_names_fr = Column(JSON, nullable=True)

    trailer_url_en = Column(String, nullable=True)
    trailer_url_fr = Column(String, nullable=True)

    overview_en = Column(String, nullable=True)
    overview_fr = Column(String, nullable=True)

    cache_update_date = Column(Date, nullable=False, default=date.today)

    def __repr__(self):
        return f"<Movie(tmdb_id : {self.tmdb_id}, cached on : {self.cache_update_date})>"
```

---

## 🎯 UserMovie

Tracks the relationship between a user and a movie with a status: `seen`, `later`, or `not_interested`.

```python
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.sql import func
from app.backend.core.database import Base

class UserMovie(Base):
    __tablename__ = "user_movies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tmdb_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (UniqueConstraint("user_id", "tmdb_id", name="_user_movie_uc"),)

    def __repr__(self):
        return f"<UserMovie(user_id={self.user_id}, tmdb_id={self.tmdb_id}, status={self.status})>"
```

---

## 💬 ChatSession

Stores the history of interactions between the user and the assistant.

```python
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime
from app.backend.core.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    conversation = Column(MutableList.as_mutable(JSON), nullable=False, default=list)
    created_on = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"Chat session {self.id} of user {self.user_id}, created on {self.created_on}"
```

---

## 🔁 Relationships (Optional)

we can Define these later.. 

**In `User`:**

```python
from sqlalchemy.orm import relationship

movies = relationship("UserMovie", backref="user", cascade="all, delete-orphan")
chats = relationship("ChatSession", backref="user", cascade="all, delete-orphan")
```

**In `CachedMovie`:**

```python
from sqlalchemy.orm import relationship

user_statuses = relationship("UserMovie", backref="movie", cascade="all, delete-orphan")
```

---

## 🧠 Design Notes

- ✅ Movie data is cached locally to reduce reliance on TMDB and OMDB.
- 🌐 All movie-related fields are multilingual: English and French.
- 🧹 Foreign keys use `ondelete="CASCADE"` for safe cleanup on user deletion.
- 🗃️ The `UserMovie` table uses a composite uniqueness constraint to avoid duplicates.
- 💬 Conversations are stored as JSON lists, preserving role-based message order and session state.

---
