from pydantic import BaseModel
from app.backend.schemas.movie_schemas import MovieCard, MovieSearchFilters
from app.backend.schemas.tvshow_schemas import TvShowCard, TvShowSearchFilters
from typing import Optional 
from typing import Literal

class ChatQuery(BaseModel):
    session_id: str
    query: str
    media_type: Optional[str]

class ChatResponse(BaseModel):
    message: str
    results: Optional[list[MovieCard | TvShowCard]] = None 
    filters: Optional[MovieSearchFilters | TvShowSearchFilters] = None
    media_type: Optional[Literal["movie", "tv"]]

