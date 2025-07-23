import pytest
from app.backend.services.llm_service import (
    parse_llm_response,
    ask_llm_for_similar_movies,
    get_llm_response
)
from app.backend.schemas.movie_schemas import MovieSearchFilters


# ------------------- parse_llm_response -------------------

def test_parse_llm_response_with_filters():
    response = """Here are some suggestions 👇

[filters]
genre_id=18, min_imdb_rating=7.0, min_release_year=2000
"""
    msg, action, movie_name, filters = parse_llm_response(response)

    assert action == "filters"
    assert filters.genre_id == 18
    assert filters.min_imdb_rating == 7.0
    assert filters.min_release_year == 2000
    assert movie_name is None
    assert "Here are some suggestions" in msg


def test_parse_llm_response_with_similar_movies():
    response = """Sure! You might like these:

[similar_movies]
movie_name = Black Swan
"""
    msg, action, movie_name, filters = parse_llm_response(response)

    assert action == "similar_movie"
    assert movie_name == "Black Swan"
    assert filters is None
    assert "you might like" in msg.lower()


def test_parse_llm_response_plain_message():
    response = "I recommend 'Arrival' or 'Ex Machina' if you like intelligent sci-fi."

    msg, action, movie_name, filters = parse_llm_response(response)

    assert msg.startswith("I recommend")
    assert action is None
    assert filters is None
    assert movie_name is None


def test_parse_llm_response_bad_filters_format():
    bad_response = """
    [filters]
    this_is_badly_formatted
    """
    msg, action, movie_name, filters = parse_llm_response(bad_response)

    assert action == "filters"
    assert filters is not None
    # All fields should be None or default
    assert filters.genre_id is None
    assert filters.min_imdb_rating is None
    assert filters.sort_by == "popularity.desc"  # default


# ------------------- ask_llm_for_similar_movies -------------------

def test_ask_llm_for_similar_movies_parsing(mocker):
    mock_response = "Get Out (2017), Us (2019), The Invitation (2015), Coherence (2013)"
    mocker.patch("app.backend.services.llm_service.get_openai_completion", return_value=mock_response)

    result = ask_llm_for_similar_movies("Get Out")
    assert isinstance(result, list)
    assert result[0] == {"title": "Get Out", "year": 2017}
    assert result[1]["title"] == "Us"
    assert result[1]["year"] == 2019


# ------------------- get_llm_response -------------------

def test_get_llm_response_calls_openai(mocker):
    mocker.patch("app.backend.services.llm_service.get_openai_completion", return_value="Sure!")
    mocker.patch("app.backend.services.llm_service.build_openai_payload", return_value=[{"role": "user", "content": "hi"}])

    conversation = [{"role": "user", "content": "hello"}]
    response = get_llm_response(conversation)

    assert response == "Sure!"
