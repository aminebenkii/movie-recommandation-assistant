from pydantic import BaseModel
from app.backend.schemas.movie_schemas import MovieCard, MovieSearchFilters
from typing import Optional


class ChatQuery(BaseModel):
    session_id: str
    query: str


class ChatResponse(BaseModel):
    message: str
    movies: Optional[list[MovieCard]]
    filters: Optional[MovieSearchFilters]
