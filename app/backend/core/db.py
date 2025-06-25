# Import SQLAlchemy functions to create the DB engine and session
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Define the path to your SQLite database file
# "sqlite:///./movies.db" means:
# → Use SQLite
# → Store the file in the current directory with the name 'movies.db'
DATABASE_URL = "sqlite:///./movies.db"

# Create the database engine using the URL above
# `connect_args={"check_same_thread": False}` is required for SQLite
# because SQLite is single-threaded and FastAPI is multi-threaded
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a SessionLocal class that will be used to create DB sessions
# - autocommit=False: changes won't be committed automatically
# - autoflush=False: changes won't be flushed automatically
# This gives you full control over when data is saved to the DB
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Create a base class from which all your models will inherit
# This Base class is used by SQLAlchemy to create tables later
Base = declarative_base()
