from fastapi import APIRouter, Depends
from app.backend.schemas.chat_schemas import ChatQuery, ChatResponse
from sqlalchemy.orm import Session
from app.backend.models.user_model import User
from app.backend.core.database import get_db
from app.backend.core.dependencies import get_current_user, get_language
from app.backend.services.chat_service import process_chat_query

router = APIRouter()

@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatQuery, 
    user: User = Depends(get_current_user), 
    database: Session = Depends(get_db),
    language: str = Depends(get_language)):

    return process_chat_query(payload, user, database, language)