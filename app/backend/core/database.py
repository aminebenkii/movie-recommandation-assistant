from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./storage/movies.db"

# Create the engine (pipe to db)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Base class for all SQLAlchemy ORM models (used with `User(Base)`)
Base = declarative_base()

# Session factory (used in routes/services to talk to the DB)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# FASTAPI routes with `Depends(get_db)`
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
