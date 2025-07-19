from pydantic import BaseModel


class UserStats(BaseModel):
    total_seen: int
    top_genres: list[str]
    average_rating_seen: float
    most_watched_years: list[int]
    average_release_year: int
    watch_later_count: int
