from pydantic import BaseModel, EmailStr
from typing import Literal


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class MediaStatusUpdate(BaseModel):
    tmdb_id: int
    status: Literal["seen", "towatchlater", "hidden", "none"]
