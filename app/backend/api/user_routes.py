# app/backend/api/user_routes.py

from fastapi import APIRouter, Depends, status, HTTPException
from app.backend.models.user_model import User
from app.backend.core.dependencies import get_current_user, get_language
from app.backend.core.database import get_db
from app.backend.schemas.user_schemas import UserPublic
from app.backend.schemas.movie_schemas import MovieCard
from app.backend.schemas.tvshow_schemas import TvShowCard
from sqlalchemy.orm import Session
from app.backend.services.user_media_service import (
    update_user_media_status, 
    get_user_media_by_status,
)
from app.backend.schemas.user_schemas import MediaStatusUpdate

router = APIRouter()

@router.get("/me", response_model=UserPublic)
def read_own_profile(user: User = Depends(get_current_user)):
    return UserPublic(
        first_name=user.first_name, last_name=user.last_name, email=user.email
    )


@router.post("/me/movies/update_status", status_code=status.HTTP_200_OK)
def update_movie_status(
    payload: MediaStatusUpdate,
    database: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    success, message = update_user_media_status("movie", payload.tmdb_id, user.id, database, payload.status)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return {"success": True}


@router.get("/me/movies/seen", response_model=list[MovieCard])
def fetch_user_seen_movies(
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
    language: str = Depends(get_language),
):
    return get_user_media_by_status("movie",user.id, database, language, "seen")


@router.get("/me/movies/towatchlater", response_model=list[MovieCard])
def fetch_user_later_movies(
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
    language: str = Depends(get_language),
):
    return get_user_media_by_status("movie", user.id, database, language, "towatchlater")


@router.get("/me/movies/hidden", response_model=list[MovieCard])
def fetch_user_hidden_movies(
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
    language: str = Depends(get_language),
):
    return get_user_media_by_status("movie", user.id, database, language, "hidden")


@router.post("/me/tvshows/update_status", status_code=status.HTTP_200_OK)
def update_tvshow_status(
    payload: MediaStatusUpdate,
    database: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    success, message = update_user_media_status("tv", payload.tmdb_id, user.id, database, payload.status)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return {"success": True}


@router.get("/me/tvshows/seen", response_model=list[TvShowCard])
def fetch_user_seen_tvshows(
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
    language: str = Depends(get_language),
):
    return get_user_media_by_status("tv",user.id, database, language, "seen")


@router.get("/me/tvshows/towatchlater", response_model=list[TvShowCard])
def fetch_user_later_tvshows(
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
    language: str = Depends(get_language),
):
    return get_user_media_by_status("tv",user.id, database, language, "towatchlater")


@router.get("/me/tvshows/hidden", response_model=list[TvShowCard])
def fetch_user_hidden_tvshows(
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
    language: str = Depends(get_language),
):
    return get_user_media_by_status("tv", user.id, database, language, "hidden")
