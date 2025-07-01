from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.backend.models.user import User
from sqlalchemy.orm import Session

from app.backend.core.security import decode_access_token
from app.backend.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token : str = Depends(oauth2_scheme) , database : Session = Depends(get_db)) -> User : 

    # decode Payload : 
    payload = decode_access_token(token)
    if payload is None : 
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # get email : 
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    # get user :
    user = database.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not Found")


