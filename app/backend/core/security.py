import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from app.backend.core.config import SECRET_KEY, ALGORITHM


def hash_password(plain_password : str) -> str:
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password:str, hashed_password:str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_in: int = 3600) -> str:

    # Make a copy of the input to avoid mutating the original
    payload = data.copy()
    # Add expiration time
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    # add expiry time to payload
    payload["exp"] = expire
    # create the token using our secret and algorithm
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> dict | None :

    try: 
        # Decode the token using secret and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError:
        return None
    