from fastapi import APIRouter, Depends
from app.backend.models.user import User
from app.backend.core.dependancies import get_current_user

router = APIRouter()

@router.get("/me")
def read_own_profile(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }
