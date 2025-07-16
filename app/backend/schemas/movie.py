from pydantic import BaseModel 
from typing import Optional, Literal


class MovieCard(BaseModel):
    tmdb_id : Optional[int]
    title: Optional[str]
    genre_names: Optional[list[str]]
    release_year: Optional[int] = None
    imdb_rating: Optional[float]
    imdb_votes_count: Optional[int]
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    overview: Optional[str]= None


class MovieListResponse(BaseModel):
    movies: list[MovieCard]


class MovieSearchFilters(BaseModel):
    genre_name: Optional[Literal[
        "action", "adventure", "animation", "comedy", "crime", "documentary",
        "drama", "family", "fantasy", "history", "horror", "music", "mystery",
        "romance", "science fiction", "tv movie", "thriller", "war", "western"
    ]] = None                                           # → convert to id
    genre_id: Optional[int] = None                      # → used for tmdb request call
    min_imdb_rating: Optional[float] = None             # → used for reranking
    min_imdb_votes_count: Optional[int] = None          # → used for reranking
    min_release_year: Optional[int] = None              # → map to primary_release_date.gte
    max_release_year: Optional[int] = None              # → map to primary_release_date.gte
    original_language: Optional[str] = None             # → map to with_original_language
    sort_by: Optional[Literal[
        "popularity.desc", 
        "vote_average.desc", 
        "vote_count.desc", 
    ]] = "popularity.desc"                              # → TMDB sort_by param



class MovieStatusUpdate(BaseModel):
    tmdb_id: int
    status: Literal["seen", "later", "not_interested", "none"]
 
