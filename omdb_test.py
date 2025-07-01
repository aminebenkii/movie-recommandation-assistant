import requests
from app.backend.core.config import OMDB_API_KEY


OMDB_BASE_URL = "http://www.omdbapi.com/"



url = OMDB_BASE_URL
params = {
        "t":  'parasite',
        "y": 2019,
        "apikey": OMDB_API_KEY,
}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()

data = response.json()

print(data)



