from fastapi import APIRouter, Depends, Request
from app.backend.schemas.movie_schemas import MovieSearchFilters, MovieCard
from app.backend.core.dependancies import get_current_user, get_db, get_language
from app.backend.models.user_model import User
from sqlalchemy.orm import Session
from app.backend.services.movie_service import recommend_movies
from app.backend.utils.utils import map_genre_to_id


router = APIRouter()


@router.post("/search", response_model=list[MovieCard])
def manual_search(
    filters: MovieSearchFilters,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    language: str = Depends(get_language),
):

    return recommend_movies(filters, user.id, db, language)
