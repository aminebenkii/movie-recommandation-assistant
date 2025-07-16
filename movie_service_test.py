from sqlalchemy.orm import Session
from app.backend.schemas.movie import MovieSearchFilters
from app.backend.services.movie_service import recommend_movies
from app.backend.core.database import SessionLocal

db: Session = SessionLocal()

filters = MovieSearchFilters(
    genre_id=35,  # Drama
    min_release_year=2010,
    max_release_year=2023,
    min_imdb_rating=7.0,
    min_imdb_votes_count=1000,
    sort_by="vote_count.desc"
)

def print_movie_card(card):
    print(f"🎬 {card.title} ({card.release_year})")
    print(f"⭐ IMDb: {card.imdb_rating} ({card.imdb_votes_count:,} votes)")
    print(f"🎭 Genres: {', '.join(card.genre_names)}")
    print(f"🎞️ Trailer: {card.trailer_url}")
    print(f"📝 {card.overview[:200]}..." if card.overview else "")
    print("—" * 60)

print("\n🇫🇷 🔥 Recommandations dramatiques (FR):\n")
movies_fr = recommend_movies(filters, user_id=1, db=db, language="fr")
for m in movies_fr[:10]:
    print_movie_card(m)

print("\n🇺🇸 🔥 Top Drama Picks (EN):\n")
movies_en = recommend_movies(filters, user_id=1, db=db, language="en")
for m in movies_en[:10]:
    print_movie_card(m)
