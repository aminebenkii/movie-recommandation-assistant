from fastapi import status, HTTPException
import logging
from sqlalchemy.orm import Session
from typing import Tuple, Optional

from app.backend.models.user_model import User
from app.backend.schemas.user_schemas import UserCreate, UserLogin, UserPublic, TokenResponse
from app.backend.core.security import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)


def handle_signup_request(user_data: UserCreate, database: Session) -> TokenResponse:

    success, message = signup_user(user_data, database)

    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    
    user_credentials = UserLogin(email=user_data.email, password=user_data.password)
    token, user = login_user(user_credentials, database)

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



def handle_login_request(user_credentials: UserLogin, database: Session) -> TokenResponse:

    token, user = login_user(user_credentials, database)

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


def signup_user(user_data: UserCreate, database: Session) -> Tuple[bool, str]:
    logger.info("Signup attempt for email: %s", user_data.email)

    email_exists = database.query(User).filter(User.email == user_data.email).first()
    if email_exists:
        logger.warning("Signup failed: email already registered - %s", user_data.email)
        return False, "Email already exists"

    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    database.add(new_user)
    database.commit()
    logger.info("User registered successfully: %s", user_data.email)
    return True, "User registered successfully"




def login_user(user_data: UserLogin, database: Session) -> Tuple[Optional[str], User]:
    logger.info("Login attempt for: %s", user_data.email)

    user = database.query(User).filter(User.email == user_data.email).first()
    if not user:
        logger.warning("Login failed: no user with email %s", user_data.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(user_data.password, user.password_hash):
        logger.warning("Login failed: wrong password for %s", user_data.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": user.email})
    logger.info("Login successful for: %s", user.email)
    return token, user