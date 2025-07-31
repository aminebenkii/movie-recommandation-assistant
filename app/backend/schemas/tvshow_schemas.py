from pydantic import BaseModel
from typing import Optional, Literal


class TvShowCard(BaseModel):
    tmdb_id: Optional[int]
    imdb_id: Optional[str]
    title: Optional[str]
    genre_names: Optional[list[str]]
    release_year: Optional[int] = None
    imdb_rating: Optional[float]
    imdb_votes_count: Optional[int]
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    overview: Optional[str] = None


class TvShowSearchFilters(BaseModel):
    genre_name: Optional[Literal[
        "action & adventure", "animation", "comedy", "crime", "documentary",
        "drama", "family", "kids", "mystery", "news", "reality",
        "sci-fi & fantasy", "soap", "talk", "war & politics", "western"
    ]] = None
    
    genre_id: Optional[int] = None
    min_imdb_rating: Optional[float] = None
    min_imdb_votes_count: Optional[int] = None
    min_release_year: Optional[int] = None
    max_release_year: Optional[int] = None
    original_language: Optional[str] = None
    sort_by: Optional[Literal[
        "popularity.desc", "vote_average.desc", "vote_count.desc"
    ]] = "popularity.desc"


class KeywordSearchRequest(BaseModel):
    keywords: str