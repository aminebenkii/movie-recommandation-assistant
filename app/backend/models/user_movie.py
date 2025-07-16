from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.sql import func
from app.backend.core.database import Base


class UserMovie(Base):

    __tablename__ = "user_movies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tmdb_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "tmdb_id", name="_user_movie_uc"),
    )

    def __repr__(self):
            return f"<UserMovie(user_id={self.user_id}, tmdb_id={self.tmdb_id}, status={self.status})>"