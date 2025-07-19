import json
from pathlib import Path

# Mappings File Directory :
ROOT_DIR = Path(__file__).resolve().parents[3]
MAPPING_FILE_PATH = ROOT_DIR / "data" / "processed" / "genres_mapping.json"


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Load Genre Mapping only once:
GENRE_MAPPING = read_json(MAPPING_FILE_PATH)


def map_genre_to_id(genre: str) -> int:
    if not genre:
        return None
    mapping = GENRE_MAPPING.get("genre_to_id")
    genre_id = mapping.get(genre.lower().strip())
    if genre_id is None:
        raise ValueError(f"Genre {genre} not found in mapping")
    return genre_id


def map_id_to_genre(id: int, language: str) -> str:
    mapping = GENRE_MAPPING.get("id_to_genre").get(language)
    genre_name = mapping.get(str(id))
    if genre_name is None:
        raise ValueError(f"Genre with id : {id}, was not found in mapping.")
    return genre_name.lower()
