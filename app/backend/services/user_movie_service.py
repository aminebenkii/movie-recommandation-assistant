from sqlalchemy.orm import Session 
from app.backend.models.user_movie import UserMovie
from app.backend.models.movie import Movie
from typing import Tuple


def update_user_movie_status(movie_id: int, user_id: int, database: Session, status: str) -> Tuple[bool, str]:
    try :
        existing_user_movie = database.query(UserMovie).where(
            UserMovie.user_id==user_id, 
            UserMovie.movie_id==movie_id).first()
        
        if status=="none":  
            if existing_user_movie:
                    database.delete(existing_user_movie)
                    database.commit()
                    return True, "Movie removed from list"
            else :
                    return True, "No entry to remove"
            
        else :
            if existing_user_movie:
                existing_user_movie.status = status         
            else :
                new_user_movie = UserMovie(user_id=user_id, movie_id=movie_id, status=status)
                database.add(new_user_movie)

            database.commit()
            return True, "Movie status updated successfully"                

    except Exception as e:
        database.rollback()
        return False, f"Database Error : {e}"


def get_moviecards_by_status(user_id: int, database: Session, status: str):

    user_movies = (
        database.query(Movie)
        .join(UserMovie, Movie.id == UserMovie.movie_id)
        .filter(UserMovie.user_id == user_id, UserMovie.status == status)
        .all()
    )

    return user_movies