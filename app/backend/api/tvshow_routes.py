# app/backend/api/tv_show_routes.py

from fastapi import APIRouter, Depends
from app.backend.schemas.tvshow_schemas import TvShowSearchFilters, TvShowCard, KeywordSearchRequest
from app.backend.core.dependencies import get_current_user, get_db, get_language
from app.backend.models.user_model import User
from sqlalchemy.orm import Session
from app.backend.services.tvshow_service import recommend_tvshows_by_filters, search_tvshows_by_title

router = APIRouter()

@router.post("/search-by-filters", response_model=list[TvShowCard])
def search_by_filters(
    filters: TvShowSearchFilters,
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
    language: str = Depends(get_language),
):

    return recommend_tvshows_by_filters(filters, user.id, database, language)


@router.post("/search-by-title", response_model=list[TvShowCard])
def search_by_keywords(
    keywords: KeywordSearchRequest,
    user: User = Depends(get_current_user),
    database: Session = Depends(get_db),
    language: str = Depends(get_language),
):

    return search_tvshows_by_title(keywords, user.id, database, language)


