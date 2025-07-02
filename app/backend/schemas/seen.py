from pydantic import BaseModel
from typing import List

class PostSeen(BaseModel):
    movie_id : int
 
class GetSeen(BaseModel):
    seen_movies: List[int]
