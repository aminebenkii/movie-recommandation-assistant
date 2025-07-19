from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.mutable import MutableList
from app.backend.core.database import Base
from datetime import datetime


class ChatSession(Base):

    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    conversation = Column(MutableList.as_mutable(JSON), nullable=False, default=list)
    created_on = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"Chat session {self.id} of user {self.user_id}, created on {self.created_on}"
