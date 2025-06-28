from fastapi import APIRouter
from app.backend.api import auth, chat, seen, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(seen.router, prefix="/seen", tags=["Seen"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])


