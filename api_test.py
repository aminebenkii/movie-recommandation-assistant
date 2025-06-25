import requests

API_KEY = "0b9217cf27ebfa83b0a8e7f6c10fb2da"
BASE_URL = "https://api.themoviedb.org/3"

def get_movies():
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "vote_count.gte": 10000,
        "vote_average.gte": 7,
        "with_genres": "35"  # Comedy
    }

    response = requests.get(url, params=params)

    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['results'])} movies\n")
        for movie in data["results"]:
            title = movie.get('title')
            rating = movie.get('vote_average')
            poster = movie.get('poster_path')
            if title and poster:
                print(f"{title} ({rating})")
                print(f"Poster: https://image.tmdb.org/t/p/w500{poster}")
                print("---")
    else:
        print("Error:", response.status_code, response.text)

get_movies()
