from app.backend.core.tmdb_client import get_genres_mapping, get_genres_reverse_mapping
from pathlib import Path
from app.backend.utils.utils import save_json

# Mappings File Directory : 
ROOT_DIR = Path(__file__).resolve().parents[3]
MAPPING_FILE_PATH = ROOT_DIR / "data" / "processed" / "genres_mapping.json"

# Fetch Genre Mappings:
mappings = {
    "genre_to_id": get_genres_mapping(),
    "id_to_genre":  get_genres_reverse_mapping()
    }

# Save mapping to json file:
save_json(MAPPING_FILE_PATH, mappings)