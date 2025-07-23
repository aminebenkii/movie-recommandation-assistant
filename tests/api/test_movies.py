import pytest

@pytest.fixture()
def user_token(client):
    payload = {
        "first_name":"Amine",
        "last_name":"Benkirane",
        "email":"ab@test.com",
        "password":"ab"
    }

    response = client.post("/auth/signup", json=payload)
    return response.json()["access_token"]



def test_movies_search_basic(client, user_token):

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept-Language": "en"
    }
    payload = {}
    
    response = client.post("/movies/search", json=payload, headers=headers)
    results = response.json()

    assert isinstance(results, list)
    assert all("title" in movie for movie in results)


def test_movies_search_with_filters(client, user_token):

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept-Language": "en"
    }
    payload = {
        "min_imdb_rating": 7.0,
        "min_imdb_votes_count": 5000,
        "min_release_year": 1990,
        "max_release_year": 2020,
        "original_language": "en",
        "sort_by": "vote_average.desc"
    }

    response = client.post("/movies/search", headers=headers, json=payload)
    assert response.status_code == 200
    results = response.json()
    assert all(movie["imdb_rating"] >= 7.0 for movie in results)


def test_movies_search_french_output(client, user_token):
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept-Language": "fr"
    }

    response = client.post("/movies/search", headers=headers, json={})
    assert response.status_code == 200
    results = response.json()

    if results:
        assert "title" in results[0]
        assert isinstance(results[0]["title"], str)


def test_movies_search_excludes_seen(client, user_token):
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept-Language": "en"
    }

    # Mark a movie as seen
    seen_payload = {"tmdb_id": 12345, "status": "seen"}
    client.post("/users/me/movies/update_status", headers=headers, json=seen_payload)

    # Search
    response = client.post("/movies/search", headers=headers, json={})
    assert response.status_code == 200

    # Check that tmdb_id 12345 is not in results
    results = response.json()
    assert all(movie["tmdb_id"] != 12345 for movie in results)
import pytest

@pytest.fixture()
def user_token(client):
    payload = {
        "first_name": "Amine",
        "last_name": "Benkirane",
        "email": "ab@test.com",
        "password": "ab"
    }

    response = client.post("/auth/signup", json=payload)
    return response.json()["access_token"]


def test_movies_search_basic(client, user_token):
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept-Language": "en"
    }

    response = client.post("/movies/search", json={}, headers=headers)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    if results:
        assert "tmdb_id" in results[0]
        assert "title" in results[0]
        assert "imdb_rating" in results[0]


def test_movies_search_with_strong_filters(client, user_token):
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept-Language": "en"
    }

    payload = {
        "min_imdb_rating": 8.5,
        "min_imdb_votes_count": 200000,
        "min_release_year": 1990,
        "max_release_year": 2020,
        "original_language": "en",
        "sort_by": "vote_average.desc"
    }

    response = client.post("/movies/search", headers=headers, json=payload)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    for movie in results:
        assert movie["imdb_rating"] >= 8.5
        assert movie["imdb_votes_count"] >= 200000


def test_movies_search_sort_by_votes(client, user_token):
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept-Language": "en"
    }

    payload = {"sort_by": "vote_count.desc"}

    response = client.post("/movies/search", headers=headers, json=payload)
    assert response.status_code == 200
    results = response.json()

    votes = [m["imdb_votes_count"] for m in results]
    assert votes == sorted(votes, reverse=True)


def test_movies_search_french_localization(client, user_token):
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept-Language": "fr"
    }

    response = client.post("/movies/search", headers=headers, json={})
    assert response.status_code == 200
    results = response.json()
    if results:
        assert "title" in results[0]
        assert isinstance(results[0]["title"], str)


def test_movies_search_excludes_seen_later_hidden(client, user_token):
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept-Language": "en"
    }

    # Mark as seen
    client.post("/users/me/movies/update_status", headers=headers, json={"tmdb_id": 101, "status": "seen"})
    # Mark as later
    client.post("/users/me/movies/update_status", headers=headers, json={"tmdb_id": 102, "status": "later"})
    # Mark as not interested
    client.post("/users/me/movies/update_status", headers=headers, json={"tmdb_id": 103, "status": "not_interested"})

    response = client.post("/movies/search", headers=headers, json={})
    assert response.status_code == 200
    tmdb_ids = [movie["tmdb_id"] for movie in response.json()]
    assert 101 not in tmdb_ids
    assert 102 not in tmdb_ids
    assert 103 not in tmdb_ids


def test_movies_search_schema(client, user_token):
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept-Language": "en"
    }

    response = client.post("/movies/search", headers=headers, json={})
    assert response.status_code == 200
    if response.json():
        movie = response.json()[0]
        assert isinstance(movie["tmdb_id"], int)
        assert isinstance(movie["title"], str)
        assert isinstance(movie["genres_names"], list)
        assert isinstance(movie["release_year"], int)
        assert isinstance(movie["imdb_rating"], float)
        assert isinstance(movie["imdb_votes_count"], int)
        assert "poster_url" in movie


def test_movies_search_empty_result(client, user_token):
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept-Language": "en"
    }

    payload = {
        "min_imdb_rating": 9.9,
        "min_imdb_votes_count": 9000000,
        "min_release_year": 2020,
        "max_release_year": 2020
    }

    response = client.post("/movies/search", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json() == []


def test_movies_search_invalid_token(client):
    headers = {
        "Authorization": "Bearer invalid.token.here",
        "Accept-Language": "en"
    }

    response = client.post("/movies/search", headers=headers, json={})
    assert response.status_code == 401


def test_movies_search_sort_switching(client, user_token):
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Accept-Language": "en"
    }

    payload_votes = {"sort_by": "vote_count.desc"}
    payload_rating = {"sort_by": "vote_average.desc"}

    r1 = client.post("/movies/search", headers=headers, json=payload_votes).json()
    r2 = client.post("/movies/search", headers=headers, json=payload_rating).json()

    if r1 and r2:
        assert r1 != r2  # Ideally, order should differ


def test_movies_search_year_range_boundaries(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}", "Accept-Language": "en"}
    payload = {
        "min_release_year": 1999,
        "max_release_year": 1999
    }

    response = client.post("/movies/search", headers=headers, json=payload)
    assert response.status_code == 200
    results = response.json()
    for movie in results:
        assert movie["release_year"] == 1999


def test_movies_search_invalid_payload_format(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}", "Accept-Language": "en"}
    bad_payload = {
        "min_imdb_rating": "not-a-number"
    }

    response = client.post("/movies/search", headers=headers, json=bad_payload)
    assert response.status_code == 422


def test_movies_search_default_language(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post("/movies/search", headers=headers, json={})
    assert response.status_code == 200
    results = response.json()
    if results:
        assert isinstance(results[0]["title"], str)


def test_movies_search_vote_count_threshold(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}", "Accept-Language": "en"}
    payload = {"min_imdb_votes_count": 100000}
    response = client.post("/movies/search", headers=headers, json=payload)
    assert response.status_code == 200
    for movie in response.json():
        assert movie["imdb_votes_count"] >= 100000
