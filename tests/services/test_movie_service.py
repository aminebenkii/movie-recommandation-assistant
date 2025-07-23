import pytest
from app.backend.services.movie_service import (
    to_movie_card, rerank_and_imdb_filter_movies, recommend_movies
)
from app.backend.models.movie_model import CachedMovie
from app.backend.models.user_movie_model import UserMovie
from app.backend.schemas.movie_schemas import MovieSearchFilters
from app.backend.schemas.movie_schemas import MovieCard
from datetime import date



# ------------------- to_movie_card -------------------

def test_to_movie_card_language_en():
    movie = CachedMovie(
        tmdb_id=1,
        title_en="Inception",
        title_fr="Origine",
        genre_names_en=["Action", "Sci-Fi"],
        genre_names_fr=["Action", "Science-Fiction"],
        release_year=2010,
        imdb_rating=8.8,
        imdb_votes_count=2000000,
        poster_url="http://example.com/poster.jpg",
        trailer_url_en="http://example.com/trailer_en.mp4",
        trailer_url_fr="http://example.com/trailer_fr.mp4",
        overview_en="A mind-bending thriller.",
        overview_fr="Un thriller hallucinant.",
    )

    card = to_movie_card(movie, language="en")
    assert card.title == "Inception"
    assert card.genre_names == ["Action", "Sci-Fi"]
    assert card.trailer_url == movie.trailer_url_en


def test_to_movie_card_language_fr():
    movie = CachedMovie(
        tmdb_id=2,
        title_en="Interstellar",
        title_fr="Interstellaire",
        genre_names_en=["Adventure", "Drama"],
        genre_names_fr=["Aventure", "Drame"],
        release_year=2014,
        imdb_rating=8.6,
        imdb_votes_count=1800000,
        poster_url="http://example.com/poster.jpg",
        trailer_url_en="http://example.com/trailer_en.mp4",
        trailer_url_fr="http://example.com/trailer_fr.mp4",
        overview_en="Space journey to save humanity.",
        overview_fr="Voyage spatial pour sauver l'humanité.",
    )

    card = to_movie_card(movie, language="fr")
    assert card.title == "Interstellaire"
    assert card.genre_names == ["Aventure", "Drame"]
    assert card.trailer_url == movie.trailer_url_fr


# ------------------- rerank_and_imdb_filter_movies -------------------

def test_rerank_and_filter_movies():
    from app.backend.services.movie_service import rerank_and_imdb_filter_movies

    movies = [
        CachedMovie(tmdb_id=1, imdb_rating=8.5, imdb_votes_count=100000),
        CachedMovie(tmdb_id=2, imdb_rating=7.0, imdb_votes_count=50000),
        CachedMovie(tmdb_id=3, imdb_rating=9.0, imdb_votes_count=200000),
    ]

    filters = MovieSearchFilters(
        min_imdb_rating=8.0,
        min_imdb_votes_count=80000,
        sort_by="vote_average.desc"
    )

    result = rerank_and_imdb_filter_movies(movies, filters)
    assert [m.tmdb_id for m in result] == [3, 1]


# ------------------- recommend_movies -------------------



def test_recommend_movies_mocked(mocker, test_db_session):
    from app.backend.services.movie_service import recommend_movies

    # Patch all external logic
    mocker.patch("app.backend.services.movie_service.map_genre_to_id", return_value=18)
    mocker.patch("app.backend.services.movie_service.fetch_unseen_tmdb_ids", return_value=[1])
    mocker.patch("app.backend.services.movie_service.get_and_cache_movies_data_to_db", return_value=None)

    mock_movie = CachedMovie(
        tmdb_id=1,
        imdb_id="tt1234567",
        imdb_rating=7.9,
        imdb_votes_count=100000,
        release_year=2020,
        poster_url="https://example.com/poster.jpg",
        title_en="Test",
        title_fr="Test FR",
        genre_ids=[18],
        genre_names_en=["drama"],
        genre_names_fr=["drame"],
        trailer_url_en="https://example.com/trailer.mp4",
        trailer_url_fr="https://example.com/trailer_fr.mp4",
        overview_en="A great movie.",
        overview_fr="Un grand film.",
        cache_update_date=date.today()
    )

    mocker.patch("app.backend.services.movie_service.fetch_movies_from_cache", return_value=[mock_movie])
    mocker.patch("app.backend.services.movie_service.rerank_and_imdb_filter_movies", return_value=[mock_movie])

    filters = MovieSearchFilters(genre_name="drama")
    result = recommend_movies(filters, user_id=1, database=test_db_session, language="en")

    assert isinstance(result, list)
    assert isinstance(result[0], MovieCard)
    assert result[0].title == "Test"
    assert result[0].genre_names == ["drama"]