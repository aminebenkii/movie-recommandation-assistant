import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.backend.services.auth_service import (
    add_user_to_db, check_user_credentials_in_db,
    handle_signup_request, handle_login_request
)
from app.backend.schemas.user_schemas import UserCreate, UserLogin
from app.backend.models.user_model import User
from app.backend.core.security import verify_password


# ---------- FIXTURES ----------

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


# ---------- add_user_to_db ----------

def test_add_user_to_db_success(fake_db, user_data):
    success, msg = add_user_to_db(user_data, fake_db)
    assert success is True
    assert msg == "User registered successfully"

    user = fake_db.query(User).filter(User.email == user_data.email).first()
    assert user is not None
    assert user.first_name == user_data.first_name
    assert verify_password(user_data.password, user.password_hash)


def test_add_user_to_db_duplicate(fake_db, user_data):
    add_user_to_db(user_data, fake_db)
    success, msg = add_user_to_db(user_data, fake_db)
    assert success is False
    assert msg == "Email already exists"


# ---------- check_user_credentials_in_db ----------

def test_check_user_credentials_success(fake_db, user_data):
    add_user_to_db(user_data, fake_db)
    creds = UserLogin(email=user_data.email, password=user_data.password)

    user = check_user_credentials_in_db(creds, fake_db)
    assert user.email == creds.email


def test_check_user_credentials_wrong_email(fake_db):
    creds = UserLogin(email="nonexistent@example.com", password="irrelevant")
    with pytest.raises(HTTPException) as exc:
        check_user_credentials_in_db(creds, fake_db)
    assert exc.value.status_code == 401
    assert "Invalid credentials" in str(exc.value.detail)


def test_check_user_credentials_wrong_password(fake_db, user_data):
    add_user_to_db(user_data, fake_db)
    creds = UserLogin(email=user_data.email, password="wrongpassword")
    with pytest.raises(HTTPException) as exc:
        check_user_credentials_in_db(creds, fake_db)
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
    creds = UserLogin(email=user_data.email, password=user_data.password)
    result = handle_login_request(creds, fake_db)
    assert result.access_token
    assert result.user.email == creds.email


def test_handle_login_request_failure(fake_db):
    creds = UserLogin(email="unknown@example.com", password="whatever")
    with pytest.raises(HTTPException) as exc:
        handle_login_request(creds, fake_db)
    assert exc.value.status_code == 401
    assert "Invalid credentials" in str(exc.value.detail)
