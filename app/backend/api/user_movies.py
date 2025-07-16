from fastapi import APIRouter, Depends, HTTPException, status
from app.backend.core.database import get_db
from app.backend.core.dependancies import get_current_user
from app.backend.models.user import User
from sqlalchemy.orm import Session
from app.backend.services.user_movie_service import update_user_movie_status
from app.backend.schemas.movie import MovieStatusUpdate


router = APIRouter()


@router.post("", status_code=status.HTTP_200_OK)
def update_status(
    payload: MovieStatusUpdate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)):

    success, message = update_user_movie_status(payload.movie_id, user.id, db, payload.status)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"message": "movie status updated"}



