from fastapi import APIRouter, Depends
from app.backend.models.user import User
from app.backend.core.dependancies import get_current_user, get_language
from app.backend.core.database import get_db
from app.backend.schemas.user import UserPublic
from app.backend.schemas.movie import MovieListResponse
from sqlalchemy.orm import Session
from app.backend.services.user_movie_service import get_user_movies_by_status


router = APIRouter()


@router.get("/me", response_model=UserPublic)
def read_own_profile(user: User = Depends(get_current_user)):
    return UserPublic(
        first_name=user.first_name, 
        last_name=user.last_name, 
        email=user.email)


@router.get("/me/movies/seen", response_model=MovieListResponse)
def fetch_user_seen_movies(
    user : User = Depends(get_current_user), 
    db: Session = Depends(get_db),
    language: str = Depends(get_language)):

    seen_movies = get_user_movies_by_status(user.id, db, language, "seen")

    return MovieListResponse(movies=seen_movies)


@router.get("/me/movies/later", response_model=MovieListResponse)
def fetch_user_later_movies(
    user : User = Depends(get_current_user), 
    db: Session = Depends(get_db),
    language: str = Depends(get_language)):

    later_movies = get_user_movies_by_status(user.id, db, language, "later")

    return MovieListResponse(movies=later_movies)


@router.get("/me/movies/not-interested", response_model=MovieListResponse)
def fetch_user_not_interested_movies(
    user : User = Depends(get_current_user), 
    db: Session = Depends(get_db),
    language: str = Depends(get_language)):

    not_interested_movies = get_user_movies_by_status(user.id, db, language, "not_interested")

    return MovieListResponse(movies=not_interested_movies)