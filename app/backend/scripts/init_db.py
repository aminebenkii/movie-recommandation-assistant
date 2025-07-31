from app.backend.core.database import Base, engine
from app.backend.models.user_model import User
from app.backend.models.user_media_model import UserMedia
from app.backend.models.chat_session_model import ChatSession
from app.backend.models.movie_model import CachedMovie
from app.backend.models.tvshow_model import CachedTvShow


def init():

    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("✅ DB recreated successfully.")


if __name__ == "__main__":
    init()
