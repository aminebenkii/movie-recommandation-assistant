from fastapi import APIRouter
from app.backend.api import auth, chat, movies, users, user_movies

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(movies.router, prefix="/movies", tags=["Movies"])
api_router.include_router(user_movies.router, prefix="/user-movies", tags=["UserMovies"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])


