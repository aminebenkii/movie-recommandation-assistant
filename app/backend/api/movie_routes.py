from fastapi import APIRouter, Depends, Request
from app.backend.schemas.movie_schemas import MovieSearchFilters, MovieCard, KeywordSearchRequest
from app.backend.core.dependencies import get_current_user, get_db, get_language
from app.backend.models.user_model import User
from sqlalchemy.orm import Session
from app.backend.services.movie_service import recommend_movies_by_filters, search_movies_by_keywords


router = APIRouter()


@router.post("/search-by-filters", response_model=list[MovieCard])
def search_by_filters(
    filters: MovieSearchFilters,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    language: str = Depends(get_language),
):

    return recommend_movies_by_filters(filters, user.id, db, language)


@router.post("/search-by-keywords", response_model=list[MovieCard])
def search_by_keywords(
    keywords: KeywordSearchRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    language: str = Depends(get_language),
):

    return search_movies_by_keywords(keywords, user.id, db, language)


