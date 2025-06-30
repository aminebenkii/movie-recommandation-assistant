from sqlalchemy import Column, Integer, String, DateTime
from app.backend.core.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable= False)
    joined = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User(id = {self.id}, name = {self.first_name} {self.last_name}, email = {self.email}, joined on : {self.joined})>"