# app/backend/api/router.py

from fastapi import APIRouter
from app.backend.api import auth_routes, chat_routes, movie_routes, tvshow_routes, user_routes

api_router = APIRouter()

api_router.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])
api_router.include_router(movie_routes.router, prefix="/movies", tags=["Movies"])
api_router.include_router(tvshow_routes.router, prefix="/tvshows", tags=["TV Shows"])
api_router.include_router(user_routes.router, prefix="/users", tags=["Users"])
