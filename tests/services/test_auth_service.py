import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.backend.services.auth_service import (
    signup_user, login_user,
    handle_signup_request, handle_login_request
)
from app.backend.schemas.user_schemas import UserCreate, UserLogin
from app.backend.models.user_model import User
from app.backend.core.security import verify_password


# ---------- FIXTURE ----------

@pytest.fixture()
def fake_db(test_db_session: Session):
    return test_db_session


@pytest.fixture()
def user_data():
    return UserCreate(
        first_name="Test",
        last_name="User",
        email="testuser@example.com",
        password="test123"
    )


# ---------- signup_user ----------

def test_signup_user_success(fake_db, user_data):
    success, msg = signup_user(user_data, fake_db)
    assert success is True
    assert msg == "User registered successfully"

    # Confirm in DB
    user = fake_db.query(User).filter(User.email == user_data.email).first()
    assert user is not None
    assert user.first_name == "Test"
    assert verify_password("test123", user.password_hash)


def test_signup_user_duplicate_email(fake_db, user_data):
    signup_user(user_data, fake_db)  # First time
    success, msg = signup_user(user_data, fake_db)  # Second time
    assert success is False
    assert msg == "Email already exists"


# ---------- login_user ----------

def test_login_user_success(fake_db, user_data):
    signup_user(user_data, fake_db)
    creds = UserLogin(email=user_data.email, password="test123")

    token, user = login_user(creds, fake_db)
    assert isinstance(token, str)
    assert user.email == user_data.email


def test_login_user_wrong_email(fake_db):
    creds = UserLogin(email="nope@example.com", password="whatever")
    with pytest.raises(HTTPException) as exc:
        login_user(creds, fake_db)
    assert exc.value.status_code == 401
    assert "Invalid credentials" in str(exc.value.detail)


def test_login_user_wrong_password(fake_db, user_data):
    signup_user(user_data, fake_db)
    creds = UserLogin(email=user_data.email, password="wrong")

    with pytest.raises(HTTPException) as exc:
        login_user(creds, fake_db)
    assert exc.value.status_code == 401
    assert "Invalid credentials" in str(exc.value.detail)


# ---------- handle_signup_request ----------

def test_handle_signup_request_success(fake_db, user_data):
    result = handle_signup_request(user_data, fake_db)
    assert result.access_token
    assert result.user.email == user_data.email


def test_handle_signup_request_duplicate(fake_db, user_data):
    handle_signup_request(user_data, fake_db)
    with pytest.raises(HTTPException) as exc:
        handle_signup_request(user_data, fake_db)
    assert exc.value.status_code == 400
    assert "Email already exists" in str(exc.value.detail)


# ---------- handle_login_request ----------

def test_handle_login_request_success(fake_db, user_data):
    handle_signup_request(user_data, fake_db)
    creds = UserLogin(email=user_data.email, password="test123")
    result = handle_login_request(creds, fake_db)
    assert result.access_token
    assert result.user.email == creds.email


def test_handle_login_request_fail(fake_db):
    creds = UserLogin(email="unknown@example.com", password="whatever")
    with pytest.raises(HTTPException) as exc:
        handle_login_request(creds, fake_db)
    assert exc.value.status_code == 401
