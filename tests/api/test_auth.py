import pytest

# ---------- SIGNUP TESTS ----------

def test_signup_success(client):
    payload = {
        "first_name": "Amine",
        "last_name": "Benkirane",
        "email": "amine@example.com",
        "password": "password123"
    }

    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == payload["email"]


def test_signup_duplicate_email(client):
    payload = {
        "first_name": "Ali",
        "last_name": "Dup",
        "email": "duplicate@example.com",
        "password": "password123"
    }

    # First signup
    client.post("/auth/signup", json=payload)

    # Second signup with same email
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 400
    assert "Email already exists" in response.json()["detail"]


def test_signup_missing_field_first_name(client):
    payload = {
        "last_name": "Benkirane",
        "email": "missing@example.com",
        "password": "password123"
    }

    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 422


def test_signup_missing_field_email(client):
    payload = {
        "first_name": "Amine",
        "last_name": "Benkirane",
        "password": "password123"
    }

    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 422


def test_signup_invalid_email_format(client):
    payload = {
        "first_name": "Amine",
        "last_name": "Benkirane",
        "email": "not-an-email",
        "password": "password123"
    }

    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 422

# ---------- LOGIN TESTS ----------

def test_login_success(client):
    payload = {
        "first_name": "Fatima",
        "last_name": "Log",
        "email": "login@example.com",
        "password": "password123"
    }

    # First, signup
    client.post("/auth/signup", json=payload)

    login_payload = {
        "email": payload["email"],
        "password": payload["password"]
    }

    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    payload = {
        "first_name": "Sara",
        "last_name": "WrongPwd",
        "email": "wrongpwd@example.com",
        "password": "correctpassword"
    }

    client.post("/auth/signup", json=payload)

    wrong_login = {
        "email": payload["email"],
        "password": "wrongpassword"
    }

    response = client.post("/auth/login", json=wrong_login)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_invalid_email(client):
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "anything"
    }

    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_missing_email(client):
    login_payload = {
        "password": "password123"
    }

    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 422


def test_login_missing_password(client):
    login_payload = {
        "email": "someone@example.com"
    }

    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 422
