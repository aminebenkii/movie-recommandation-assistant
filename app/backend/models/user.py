from sqlalchemy import Column, Integer, String
from app.backend.core.database import Base


class User(Base):
    
    __tablename_ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable= False)


