from fastapi import APIRouter, Depends, HTTPException, status
from app.backend.core.database import get_db
from app.backend.core.dependancies import get_current_user
from app.backend.models.user import User
from sqlalchemy.orm import Session
from app.backend.services.seen_service import mark_movie_as_seen
from app.backend.schemas.seen import PostSeen


router = APIRouter()


@router.get("/seen")
def get_seen():
    return {"message" : "Seen Movies" }


@router.post("/seen", status_code=status.HTTP_200_OK)
def post_seen(
    payload :PostSeen, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)):

    success, message = mark_movie_as_seen(payload.movie_id, db, user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {"message": "movie added to seen list"}