from fastapi import APIRouter, Depends, status, HTTPException
from app.backend.models.user_model import User
from app.backend.core.dependencies import get_current_user, get_language
from app.backend.core.database import get_db
from app.backend.schemas.user_schemas import UserPublic
from app.backend.schemas.movie_schemas import MovieCard
from sqlalchemy.orm import Session
from app.backend.services.user_movie_service import get_user_movies_by_status
from app.backend.services.user_movie_service import update_user_movie_status
from app.backend.schemas.movie_schemas import MovieStatusUpdate

router = APIRouter()

@router.get("/me", response_model=UserPublic)
def read_own_profile(user: User = Depends(get_current_user)):
    return UserPublic(
        first_name=user.first_name, last_name=user.last_name, email=user.email
    )


@router.post("me/movies/update_status", status_code=status.HTTP_200_OK)
def update_status(
    payload: MovieStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    success, message = update_user_movie_status(payload.tmdb_id, user.id, db, payload.status)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return {"message": "movie status updated"}


@router.get("/me/movies/seen", response_model=list[MovieCard])
def fetch_user_seen_movies(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    language: str = Depends(get_language),
):
    return get_user_movies_by_status(user.id, db, language, "seen")


@router.get("/me/movies/towatchlater", response_model=list[MovieCard])
def fetch_user_later_movies(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    language: str = Depends(get_language),
):
    return get_user_movies_by_status(user.id, db, language, "towatchlater")


@router.get("/me/movies/hidden", response_model=list[MovieCard])
def fetch_user_not_interested_movies(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    language: str = Depends(get_language),
):
    return get_user_movies_by_status(user.id, db, language, "hidden")
