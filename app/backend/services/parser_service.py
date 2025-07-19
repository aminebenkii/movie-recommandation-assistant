from app.backend.schemas.movie_schemas import MovieSearchFilters


def parse_filter_line(line: str) -> MovieSearchFilters:
    line = line.replace("[filters_requested]", "").strip()
    parts = line.split(",")
    filter_kwargs = {}

    for part in parts:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key == "genre_name":
            filter_kwargs["genre_name"] = value.lower()
        elif key == "min_imdb_rating":
            filter_kwargs["min_imdb_rating"] = float(value)
        elif key == "min_imdb_votes":
            filter_kwargs["min_imdb_votes"] = int(value)
        elif key == "min_release_year":
            filter_kwargs["min_release_year"] = int(value)
        elif key == "origin_country":
            filter_kwargs["origin_country"] = value.upper()
        elif key == "response_language":
            filter_kwargs["response_language"] = value.lower()

    return MovieSearchFilters(**filter_kwargs)
