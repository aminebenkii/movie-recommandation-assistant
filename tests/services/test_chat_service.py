import pytest
from unittest.mock import MagicMock
from app.backend.schemas.chat_schemas import ChatQuery
from app.backend.services.chat_service import process_chat_query
from app.backend.schemas.movie_schemas import MovieCard, MovieSearchFilters
from app.backend.models.user_model import User
from uuid import uuid4


@pytest.fixture()
def user(test_db_session):
    user = User(
        first_name="Test",
        last_name="Chat",
        email="chat@example.com",
        password_hash="hashed"
    )
    test_db_session.add(user)
    test_db_session.commit()
    return user




# 3. Plain chat with no action
def test_chat_with_plain_response(mocker, test_db_session, user):
    mocker.patch("app.backend.services.chat_service.get_llm_response", return_value="I recommend 'Her' and 'Ex Machina'.")
    mocker.patch("app.backend.services.chat_service.parse_llm_response", return_value=(
        "I recommend 'Her' and 'Ex Machina'.", None, None, None
    ))

    payload = ChatQuery(session_id=str(uuid4()), query="Good modern sci-fi?")
    result = process_chat_query(payload, user, test_db_session, "en")

    assert result.message.startswith("I recommend")
    assert result.movies is None
    assert result.filters is None


# 4. Ensure a new session is created
def test_chat_creates_new_session(test_db_session, user):
    from app.backend.models.chat_session_model import ChatSession
    session_id = str(uuid4())

    # Ensure session doesn't exist before
    assert test_db_session.query(ChatSession).filter_by(id=session_id).first() is None

    from app.backend.services.chat_service import get_or_create_chat_session
    session = get_or_create_chat_session(user.id, session_id, test_db_session)
    assert session.id == session_id
    assert session.user_id == user.id

    # Should now exist in DB
    exists = test_db_session.query(ChatSession).filter_by(id=session_id).first()
    assert exists is not None


# 5. Test appending to conversation
def test_chat_appends_to_existing_session(mocker, test_db_session, user):
    from app.backend.services.chat_service import get_or_create_chat_session
    session_id = str(uuid4())
    session = get_or_create_chat_session(user.id, session_id, test_db_session)

    # Manually seed 1 message
    session.conversation.append({"role": "user", "content": "Hi"})
    test_db_session.commit()

    mocker.patch("app.backend.services.chat_service.get_llm_response", return_value="Okay!")
    mocker.patch("app.backend.services.chat_service.parse_llm_response", return_value=(
        "Okay!", None, None, None
    ))

    payload = ChatQuery(session_id=session_id, query="Hello again")
    result = process_chat_query(payload, user, test_db_session, "en")

    assert result.message == "Okay!"

    # Make sure conversation now has 3 messages: user, assistant, user again
    session = get_or_create_chat_session(user.id, session_id, test_db_session)
    assert len(session.conversation) == 3
