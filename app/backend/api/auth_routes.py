from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.backend.core.database import get_db
from app.backend.schemas.user_schemas import UserCreate, UserLogin, TokenResponse
from app.backend.services.auth_service import handle_login_request, handle_signup_request


router = APIRouter()


@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
def login(user_credentials: UserLogin, database: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    """
    return handle_login_request(user_credentials, database)


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
def signup(user_data: UserCreate, database: Session = Depends(get_db)):
    """
    Signup user and return JWT token.
    """

    return handle_signup_request(user_data, database)
