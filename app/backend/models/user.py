from pydantic import BaseModel

class user(BaseModel):
    user_id: str
    username: str
    hashed_password:str

