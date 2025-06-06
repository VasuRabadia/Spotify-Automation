from flask import Blueprint, session, jsonify
import requests

tracks_bp = Blueprint("playlist_tracks", __name__)


@tracks_bp.route("/playlist/<playlist_id>/tracks")
def get_playlist_tracks(playlist_id):
    access_token = session.get("access_token")
    if not access_token:
        return jsonify({"error": "Access token not found. Authorize via /home"}), 401

    headers = {"Authorization": f"Bearer {access_token}"}
    if playlist_id == "1":
        url = f"https://api.spotify.com/v1/me/tracks?limit=50"
    else:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=100"

    all_tracks = []

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return (
                jsonify(
                    {
                        "error": "Failed to fetch playlist tracks",
                        "details": response.json(),
                    }
                ),
                response.status_code,
            )

        # print("Spotify raw response:", response.json())

        data = response.json()
        all_tracks.extend(data.get("items", []))
        url = data.get("next")

    # Optionally extract just track names
    track_info = []
    for item in all_tracks:
        track = item.get("track")
        if track:
            track_info.append(
                {
                    "name": track.get("name"),
                    "artist": [artist["name"] for artist in track.get("artists", [])],
                    "id": track.get("id"),
                    "url": track.get("external_urls", {}).get("spotify"),
                }
            )

    # print(f"BEFORE_RETURN_TRACK_INFO: {track_info}")

    return jsonify(track_info)
