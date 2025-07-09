from typing import Tuple, Optional
from sqlalchemy.orm import Session
from app.backend.models.user import User
from app.backend.schemas.user import UserCreate, UserLogin
from app.backend.core.security import hash_password, verify_password, create_access_token


def register_user(user_data: UserCreate, database: Session) -> Tuple[bool, str]:
    
    # check if the email already exists :
    email_exists =  database.query(User).filter(User.email == user_data.email).first()
    if email_exists : 
        return False, "Email already exists"

    new_user = User(
        first_name = user_data.first_name,
        last_name = user_data.last_name,
        email = user_data.email,
        password_hash = hash_password(user_data.password)
    )

    database.add(new_user)
    database.commit()

    return True, "User registered successfully"



def login_user(user_data: UserLogin, database: Session) -> Optional[str]:

    # fetch user in the database:
    user = database.query(User).filter(User.email == user_data.email).first()

    if not user :
        return None

    if not verify_password(user_data.password, user.password_hash):
        return None

    token = create_access_token({"sub": user.email})
    return token


















