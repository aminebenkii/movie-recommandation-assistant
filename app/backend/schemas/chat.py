from pydantic import BaseModel
from app.backend.schemas.movie import MovieCard, MovieSearchFilters
from typing import Optional

class ChatQuery(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    message: str
    movies: list[MovieCard]
    filters: Optional[MovieSearchFilters]

