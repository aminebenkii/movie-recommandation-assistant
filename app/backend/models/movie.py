from sqlalchemy import Column, String, Integer, Float, Date, JSON
from sqlalchemy.orm import Session
from app.backend.core.database import Base
from datetime import date


class CachedMovie(Base):

    __tablename__ = "movies"

    id = Column(Integer,primary_key=True, index=True )
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


