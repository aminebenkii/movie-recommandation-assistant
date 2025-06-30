from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.backend.core.database import Base


class SeenMovie(Base):

    __tablename__ = "seen_movies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    movie_id = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="_user_movie_uc"),
    )

    def __repr__(self):
        return f"<User {self.user_id} saw Movie{self.movie_id}>"