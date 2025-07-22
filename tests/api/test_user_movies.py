import pytest

@pytest.fixture
def user_token(client):
    signup_data = {
        "first_name": "Movie",
        "last_name": "Lover",
        "email": "lover@example.com",
        "password": "password123"
    }
    response = client.post("/auth/signup", json=signup_data)
    return response.json()["access_token"]


def test_mark_movie_as_seen(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {"tmdb_id": 12345, "status": "seen"}
    response = client.post("/users/me/movies/update_status", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_mark_movie_as_watch_later(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {"tmdb_id": 12345, "status": "towatchlater"}
    response = client.post("/users/me/movies/update_status", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_mark_movie_as_not_interested(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {"tmdb_id": 12345, "status": "hidden"}
    response = client.post("/users/me/movies/update_status", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_remove_movie_status(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {"tmdb_id": 12345, "status": "none"}
    response = client.post("/users/me/movies/update_status", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
