from typing import Tuple
from sqlalchemy.orm import Session
from app.backend.models.user_media_model import UserMedia

# these may stay separate for now
from app.backend.schemas.movie_schemas import MovieCard
from app.backend.services.movie_service import fetch_movies_from_cache, to_movie_card
from app.backend.services.tvshow_service import fetch_tvshows_from_cache, to_tvshow_card
from app.backend.schemas.tvshow_schemas import TvShowCard



def update_user_media_status(
    media_type: str, tmdb_id: int, user_id: int, database: Session, status: str
) -> Tuple[bool, str]:
    """
    Updates or deletes a user's media status (seen, hidden, etc.)
    """
    try:
        existing = (
            database.query(UserMedia)
            .filter(
                UserMedia.media_type == media_type,
                UserMedia.user_id == user_id,
                UserMedia.tmdb_id == tmdb_id,
            )
            .first()
        )

        if status == "none":
            if existing:
                database.delete(existing)
                database.commit()
                return True, f"{media_type.title()} removed from list"
            else:
                return True, "No entry to remove"

        if existing:
            existing.status = status
        else:
            database.add(UserMedia(
                media_type=media_type,
                user_id=user_id,
                tmdb_id=tmdb_id,
                status=status
            ))

        database.commit()
        return True, f"{media_type.title()} status updated successfully"

    except Exception as e:
        database.rollback()
        return False, f"Database Error: {e}"
    

def get_user_media_by_status(
    media_type: str,
    user_id: int,
    database: Session,
    language: str,
    status: str
) -> list[MovieCard | TvShowCard]:
    """
    Fetches cached media of a given type + status for the user.
    Returns MovieCard or TvShowCard list.
    """
    user_media = (
        database.query(UserMedia)
        .filter(
            UserMedia.user_id == user_id,
            UserMedia.status == status,
            UserMedia.media_type == media_type,
        )
        .all()
    )

    listed_ids = [m.tmdb_id for m in user_media]

    if media_type == "movie":
        cached = fetch_movies_from_cache(listed_ids, database)
        return [to_movie_card(m, language) for m in cached]
    
    elif media_type == "tv":
        cached = fetch_tvshows_from_cache(listed_ids, database)
        return [to_tvshow_card(m, language) for m in cached]

    else:
        return []  
