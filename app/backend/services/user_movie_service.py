from typing import Tuple
from sqlalchemy.orm import Session
from app.backend.models.user_movie_model import UserMovie
from app.backend.schemas.movie_schemas import MovieCard
from app.backend.services.movie_service import fetch_movies_from_cache, to_movie_card


def update_user_movie_status(
    tmdb_id: int, user_id: int, database: Session, status: str
) -> Tuple[bool, str]:

    print(tmdb_id, user_id, status)
    try:
        existing_user_movie = (
            database.query(UserMovie)
            .where(UserMovie.user_id == user_id, UserMovie.tmdb_id == tmdb_id)
            .first()
        )

        if status == "none":
            if existing_user_movie:
                database.delete(existing_user_movie)
                database.commit()
                return True, "Movie removed from list"
            else:
                return True, "No entry to remove"

        else:
            if existing_user_movie:
                existing_user_movie.status = status
            else:
                new_user_movie = UserMovie(
                    user_id=user_id, tmdb_id=tmdb_id, status=status
                )
                database.add(new_user_movie)

            database.commit()
            return True, "Movie status updated successfully"

    except Exception as e:
        database.rollback()
        return False, f"Database Error : {e}"


def get_user_movies_by_status(
    user_id: int, database: Session, language: str, status: str
) -> list[MovieCard]:

    user_movies = (
        database.query(UserMovie)
        .filter(UserMovie.user_id == user_id, UserMovie.status == status)
        .all()
    )

    listed_ids = [m.tmdb_id for m in user_movies]
    cache_movies = fetch_movies_from_cache(listed_ids, database)

    return [to_movie_card(m, language) for m in cache_movies]
