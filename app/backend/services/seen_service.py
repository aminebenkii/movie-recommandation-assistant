from sqlalchemy.orm import Session 
from app.backend.models.seen import SeenMovie


def mark_movie_as_seen(movie_id: int, database: Session, user_id: int):

    alredy_marked_seen = database.query(SeenMovie).filter(
        SeenMovie.movie_id == movie_id,
        SeenMovie.user_id == user_id
        ).first()
    
    if alredy_marked_seen :
        return False, "Movie Already Marked as seen for user"

    try:
        seen_movie = SeenMovie(user_id = user_id, movie_id = movie_id)
        database.add(seen_movie)
        database.commit()
        return True, "Movie added to user's seen database successfully"

    except Exception as e:
        database.rollback()
        return False, "Database error while saving seen movie"

   