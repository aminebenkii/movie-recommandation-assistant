from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.backend.core.database import get_db
from app.backend.schemas.user import UserCreate, UserLogin, TokenResponse
from app.backend.services.auth_service import register_user, login_user


router = APIRouter()


@router.post("/register", status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    success, message = register_user(user_data, db)
    if not success :
        raise HTTPException(status_code=400, detail=message) 
    return {"message":"User Registered Successfully"}
    

@router.post("/login", status_code=200, response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    token = login_user(user_data, db)
    if not token :
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return {
            "access_token": token,
            "token_type": "bearer"
    }





































