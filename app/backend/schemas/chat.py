from pydantic import BaseModel
from typing import List
from app.backend.schemas.movie import MovieCard


class ChatRequest(BaseModel):

    session_id: str
    message: str


class ChatResponse(BaseModel):

    response: str
    update_movie_panel: bool = False
    recommended_movies: List[MovieCard] = []
