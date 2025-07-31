from app.backend.core.tmdb_client import get_genres_mapping
from pathlib import Path
from app.backend.utils.utils import save_json

# Mappings File Directory :
ROOT_DIR = Path(__file__).resolve().parents[3]
MAPPING_FILE_PATH = ROOT_DIR / "data" / "processed" / "genres_mapping.json"


# Fetch Genre Mappings:
movie_mappings_en = get_genres_mapping("movie", "en")
movie_mappings_fr = get_genres_mapping("movie", "fr")
tvshow_mappings_en = get_genres_mapping("tv", "en")
tvshow_mappings_fr = get_genres_mapping("tv", "fr")

genres_mappings = {
                    "movie": {
                            "en": movie_mappings_en,
                            "fr": movie_mappings_fr
                        },

                    "tv": {
                            "en": tvshow_mappings_en,
                            "fr": tvshow_mappings_fr
                        }
                }

# Save mapping to json file:
save_json(MAPPING_FILE_PATH, genres_mappings)
