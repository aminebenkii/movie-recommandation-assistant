import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.backend.core.database import Base
from app.backend.main import app



from app.backend.core.dependencies import get_db
import gc 

# Step 1: Define a file-based DB
TEST_DB_PATH = "tests/test.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Step 2: Override dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Step 3: Setup DB schema and override FastAPI dependency
@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    # Remove old DB file if it exists
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Override get_db for all tests
    app.dependency_overrides[get_db] = override_get_db

    # Yield so tests can run
    yield

    # ✅ CLEAN TEARDOWN
    engine.dispose()
    gc.collect()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


# Direct DB session for testing services (bypasses FastAPI)
@pytest.fixture()
def test_db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        

# Step 4: Create FastAPI test client
@pytest.fixture()
def client():
    return TestClient(app)
