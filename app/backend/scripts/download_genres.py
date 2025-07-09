from app.backend.core.tmdb_client import get_genres_mapping
from pathlib import Path
from app.backend.utils.utils import save_json

# Mappings File Directory : 
ROOT_DIR = Path(__file__).resolve().parents[3]
MAPPING_FILE_PATH = ROOT_DIR / "data" / "processed" / "genres_mapping.json"

# Fetch Genre Mappings:
mappings = get_genres_mapping()

# Save mapping to json file:
save_json(MAPPING_FILE_PATH, mappings)
