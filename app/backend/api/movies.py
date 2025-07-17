from fastapi import APIRouter, Depends, status, Request
from app.backend.schemas.movie import MovieSearchFilters, MovieCard
from app.backend.core.dependancies import get_current_user, get_db, get_language
from app.backend.models.user import User
from sqlalchemy.orm import Session
from app.backend.services.movie_service import recommend_movies
from app.backend.utils.utils import map_genre_to_id


router = APIRouter()


@router.post("/search", response_model=list[MovieCard])
def manual_search(
    filters: MovieSearchFilters,
    request: Request,  # ✅ This gives you access to raw headers
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    language: str = Depends(get_language)
):
    print("📩 Incoming headers:")
    for key, value in request.headers.items():
        print(f"  {key}: {value}")

    print("🌐 Parsed language from header:", language)

    filters.genre_id = map_genre_to_id(filters.genre_name)
    movie_cards = recommend_movies(filters, user.id, db, language)

    return movie_cards