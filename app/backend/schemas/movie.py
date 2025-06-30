from pydantic import BaseModel 
from typing import Optional, List

class MovieCard(BaseModel):
    id : int
    title: str
    genres: List[str]
    rating: float
    votes: int
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    overview: Optional[str]= None

