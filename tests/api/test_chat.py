import pytest
from uuid import uuid4

@pytest.fixture()
def chat_user_token(client):
    payload = {
        "first_name": "Chat",
        "last_name": "Tester",
        "email": "chat@test.com",
        "password": "secure123"
    }
    response = client.post("/auth/signup", json=payload)
    return response.json()["access_token"]

@pytest.fixture()
def session_id():
    return str(uuid4())


# 1. Basic chat response with message
def test_chat_basic_query_response(client, chat_user_token, session_id):
    headers = {
        "Authorization": f"Bearer {chat_user_token}",
        "Accept-Language": "en"
    }
    payload = {
        "session_id": session_id,
        "query": "Suggest me a sci-fi movie"
    }

    response = client.post("/chat", json=payload, headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)


# 2. Chat returns movies + filters (LLM-powered)
def test_chat_returns_movies_and_filters(client, chat_user_token, session_id):
    headers = {
        "Authorization": f"Bearer {chat_user_token}",
        "Accept-Language": "en"
    }
    payload = {
        "session_id": session_id,
        "query": "Show me underrated sci-fi from the 90s"
    }

    response = client.post("/chat", json=payload, headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert "message" in data

    if data.get("movies"):
        assert isinstance(data["movies"]["movies"], list)
        assert "title" in data["movies"]["movies"][0]

    if data.get("filters"):
        assert "min_release_year" in data["filters"]
        assert "genre_id" in data["filters"] or "genre_name" in data["filters"]


# 3. Invalid JWT token
def test_chat_invalid_token(client, session_id):
    headers = {
        "Authorization": "Bearer faketoken.invalid",
        "Accept-Language": "en"
    }
    payload = {
        "session_id": session_id,
        "query": "What thriller should I watch?"
    }

    response = client.post("/chat", json=payload, headers=headers)
    assert response.status_code == 401


# 4. Missing fields in payload
def test_chat_missing_query_field(client, chat_user_token):
    headers = {"Authorization": f"Bearer {chat_user_token}"}
    payload = {"session_id": str(uuid4())}  # missing query

    response = client.post("/chat", json=payload, headers=headers)
    assert response.status_code == 422


def test_chat_missing_session_id_field(client, chat_user_token):
    headers = {"Authorization": f"Bearer {chat_user_token}"}
    payload = {"query": "Show me a good drama"}  # missing session_id

    response = client.post("/chat", json=payload, headers=headers)
    assert response.status_code == 422


# 5. French language test
def test_chat_french_language_reply(client, chat_user_token, session_id):
    headers = {
        "Authorization": f"Bearer {chat_user_token}",
        "Accept-Language": "fr"
    }
    payload = {
        "session_id": session_id,
        "query": "Des films policiers intelligents"
    }

    response = client.post("/chat", json=payload, headers=headers)
    assert response.status_code == 200
    assert "message" in response.json()


# 6. Optional — Simulate chat context memory (re-using session)
def test_chat_context_memory(client, chat_user_token, session_id):
    headers = {
        "Authorization": f"Bearer {chat_user_token}",
        "Accept-Language": "en"
    }

    # Initial question
    client.post("/chat", json={
        "session_id": session_id,
        "query": "I like sci-fi movies"
    }, headers=headers)

    # Follow-up
    followup = client.post("/chat", json={
        "session_id": session_id,
        "query": "What else do you recommend?"
    }, headers=headers)

    assert followup.status_code == 200
    assert "message" in followup.json()


# 7. Mock LLM response (ready when mocking is enabled)
"""
def test_chat_with_mocked_llm_response(client, chat_user_token, session_id, mocker):
    mock_openai = mocker.patch("app.backend.services.llm_service.ask_llm_for_similar_movies")
    mock_openai.return_value = [{"title": "Moon", "year": 2009}]

    headers = {
        "Authorization": f"Bearer {chat_user_token}",
        "Accept-Language": "en"
    }
    payload = {
        "session_id": session_id,
        "query": "More like Interstellar"
    }

    response = client.post("/chat", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "Moon" in data["message"]
"""
