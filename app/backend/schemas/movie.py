from pydantic import BaseModel 
from typing import Optional, List, Literal


class MovieSearchFilter(BaseModel):

    genre_name: Literal[
        "action", "adventure", "animation", "comedy", "crime", "documentary",
        "drama", "family", "fantasy", "history", "horror", "music", "mystery",
        "romance", "science fiction", "tv movie", "thriller", "war", "western"
    ]                                                   # → convert to id
    genre_id: Optional[int] = None                      # → used for tmdb request call
    min_imdb_rating: Optional[float] = None             # → used for reranking
    min_imdb_votes: Optional[int] = None                # → used for reranking
    min_release_year: Optional[int] = None              # → map to primary_release_date.gte
    origin_country: Optional[str] = None                # → map to with_origin_country
    response_language: Optional[str] = None             # → map to language


class MovieCard(BaseModel):
    
    id : int
    title: str
    genre_names: List[str]
    imdb_rating: float
    imdb_votes: int
    release_year: Optional[int] = None
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    overview: Optional[str]= None

