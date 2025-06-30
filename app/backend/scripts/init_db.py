from app.backend.core.database import Base, engine
from app.backend.models.user import User
from app.backend.models.seen import SeenMovie

def init():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("✅ DB recreated successfully.")

if __name__ == "__main__":
    init()
