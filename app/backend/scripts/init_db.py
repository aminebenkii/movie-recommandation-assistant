from app.backend.core.database import Base, engine
from app.backend.models.user import User

def init():

    print("Creating db")
    Base.metadata.create_all(bind=engine)
    print("DB Created Successfully")

if __name__ == "__main__":
    init()