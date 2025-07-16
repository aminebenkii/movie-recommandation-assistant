from fastapi import APIRouter, Depends, status
from app.backend.schemas.movie import MovieSearchFilters, MovieListResponse
from app.backend.core.dependancies import get_current_user, get_db, get_language
from app.backend.models.user import User
from sqlalchemy.orm import Session
from app.backend.services.movie_service import recommend_movies


router = APIRouter()

@router.post("/search", response_model=MovieListResponse)
def manual_search(
    filters: MovieSearchFilters, 
    user: User = Depends(get_current_user),
    db : Session = Depends(get_db), 
    language= Depends(get_language)):

    movie_cards = recommend_movies(filters, user.id, db, language)

    return MovieListResponse(movies=movie_cards)