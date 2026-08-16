import os
import json
from datetime import datetime, timezone

import requests

TOKEN = os.getenv("TMDB_API_KEY_FOR_MOVIE")

if not TOKEN:
    raise RuntimeError("TMDB_API_KEY_FOR_MOVIE secret is missing.")

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
}


def get(endpoint):
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers=HEADERS,
        params={
            "language": "en-US"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()["results"]


def convert(items):
    result = []

    for item in items:
        result.append({
            "id": item["id"],
            "title": item.get("name") or item.get("title"),
            "rating": item.get("vote_average"),
            "votes": item.get("vote_count"),
            "overview": item.get("overview"),
            "poster": IMAGE_BASE + item["poster_path"] if item.get("poster_path") else None,
            "backdrop": IMAGE_BASE + item["backdrop_path"] if item.get("backdrop_path") else None,
            "release": item.get("first_air_date") or item.get("release_date")
        })

    return result


data = {
    "updated": datetime.now(timezone.utc).isoformat(),

    "trending": convert(get("trending/movie/day")[:12]),

    "popular": convert(get("movie/popular")[:12]),

    "top_rated": convert(get("movie/top_rated")[:12])

}

os.makedirs("data", exist_ok=True)

with open("data/tmdb.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("TMDB data updated successfully.")
