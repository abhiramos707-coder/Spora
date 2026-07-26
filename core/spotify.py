import requests

def get_recently_played(access_token, limit=5):
    url = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return []

    data = response.json()

    songs = []

    for item in data.get("items", []):
        track = item["track"]

        songs.append({
            "name": track["name"],
            "artist": ", ".join(a["name"] for a in track["artists"]),
            "album_image": track["album"]["images"][-1]["url"],
            "played_at": item["played_at"]
        })

    return songs