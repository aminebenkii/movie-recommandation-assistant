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

# ---------- UPDATE STATUS TESTS ----------

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


def test_mark_movie_as_hidden(client, user_token):
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


def test_overwrite_movie_status(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    payload_seen = {"tmdb_id": 12345, "status": "seen"}
    payload_later = {"tmdb_id": 12345, "status": "towatchlater"}

    # Set as seen
    client.post("/users/me/movies/update_status", json=payload_seen, headers=headers)

    # Overwrite with towatchlater
    response = client.post("/users/me/movies/update_status", json=payload_later, headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True


"""
# ---------- GET MOVIE LISTS TESTS ----------

def test_get_seen_movies(client, user_token):
    headers = {
    "Authorization": f"Bearer {user_token}",
    "Accept-Language": "en"
    }
    client.post("/users/me/movies/update_status", json={"tmdb_id": 603, "status": "seen"}, headers=headers)

    response = client.get("/users/me/movies/seen", headers=headers)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert any(movie["tmdb_id"] == 603 for movie in results)


def test_get_watch_later_movies(client, user_token):
    headers = {
    "Authorization": f"Bearer {user_token}",
    "Accept-Language": "en"
    }
    client.post("/users/me/movies/update_status", json={"tmdb_id": 603, "status": "towatchlater"}, headers=headers)

    response = client.get("/users/me/movies/towatchlater", headers=headers)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert any(movie["tmdb_id"] == 603 for movie in results)


def test_get_hidden_movies(client, user_token):
    headers = {
    "Authorization": f"Bearer {user_token}",
    "Accept-Language": "en"
    }
    client.post("/users/me/movies/update_status", json={"tmdb_id": 603, "status": "hidden"}, headers=headers)

    response = client.get("/users/me/movies/hidden", headers=headers)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert any(movie["tmdb_id"] == 603 for movie in results)


def test_removed_movie_is_not_in_any_list(client, user_token):
    headers = {
    "Authorization": f"Bearer {user_token}",
    "Accept-Language": "en"
    }
    client.post("/users/me/movies/update_status", json={"tmdb_id": 603, "status": "seen"}, headers=headers)
    client.post("/users/me/movies/update_status", json={"tmdb_id": 603, "status": "none"}, headers=headers)

    seen = client.get("/users/me/movies/seen", headers=headers).json()
    later = client.get("/users/me/movies/towatchlater", headers=headers).json()
    hidden = client.get("/users/me/movies/hidden", headers=headers).json()

    assert all(603 not in [m["tmdb_id"] for m in lst] for lst in [seen, later, hidden])

    """