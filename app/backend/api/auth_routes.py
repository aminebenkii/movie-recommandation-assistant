from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.backend.core.database import get_db
from app.backend.schemas.user_schemas import UserCreate, UserLogin, UserPublic, TokenResponse
from app.backend.services.auth_service import signup_user, login_user

router = APIRouter()

@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    token, user = login_user(user_credentials, db)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )
    return TokenResponse(
        access_token=token,
        token_type="Bearer",
        user=UserPublic(
            first_name=user.first_name, last_name=user.last_name, email=user.email
        ),
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    success, message = signup_user(user_data, db)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    user_credentials = UserLogin(email=user_data.email, password=user_data.password)
    token, user = login_user(user_credentials, db)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )
    return TokenResponse(
        access_token=token,
        token_type="Bearer",
        user=UserPublic(
            first_name=user.first_name, last_name=user.last_name, email=user.email
        ),
    )
