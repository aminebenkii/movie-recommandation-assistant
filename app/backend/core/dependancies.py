from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.backend.models.user import User
from sqlalchemy.orm import Session

from app.backend.core.security import decode_access_token
from app.backend.core.database import get_db

oauth2_scheme = HTTPBearer()

def get_current_user(token : HTTPAuthorizationCredentials = Depends(oauth2_scheme) , database : Session = Depends(get_db)) -> User : 

    # decode Payload : 
    payload = decode_access_token(token.credentials.replace("Bearer ", ""))

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

    return user



def get_language(accept_language: str = Header(default="en", convert_underscores=False)) -> str:
    """
    Extracts the language preference from the Accept-Language header.
    Supports 'en' or 'fr'. Defaults to 'en'.
    
    lang = accept_language.lower().split(",")[0].strip()
    if lang.startswith("fr"):
        return "fr"
    """
    return "en"
