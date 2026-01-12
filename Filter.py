import requests
import string
from youtube_search import YoutubeSearch
import json
import os
import urllib.parse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Initialize Spotify client
def get_spotify_client():
    """Get authenticated Spotify client"""
    client_id = os.environ.get('SPOTIPY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')

    if not client_id or not client_secret:
        return None

    try:
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        print(f"Spotify auth error: {e}")
        return None


def search_spotify(query, limit=5):
    """Search Spotify for songs and return results for autocomplete"""
    sp = get_spotify_client()
    if not sp:
        return []

    try:
        results = sp.search(q=query, type='track', limit=limit)
        tracks = []

        for track in results['tracks']['items']:
            # Get the largest album image
            images = track['album']['images']
            image_url = images[0]['url'] if images else None

            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'image': image_url,
                'display': f"{track['name']} - {track['artists'][0]['name']}"
            })

        return tracks
    except Exception as e:
        print(f"Spotify search error: {e}")
        return []


def get_track_details(track_id):
    """Get full track details from Spotify by ID"""
    sp = get_spotify_client()
    if not sp:
        return None

    try:
        track = sp.track(track_id)
        images = track['album']['images']
        image_url = images[0]['url'] if images else None

        return {
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'image': image_url
        }
    except Exception as e:
        print(f"Spotify track error: {e}")
        return None


def lyric(artist, song):
    """Fetch lyrics from lyrics.ovh API"""
    try:
        # URL encode the artist and song
        artist_encoded = urllib.parse.quote(artist.strip())
        song_encoded = urllib.parse.quote(song.strip())

        response = requests.get(
            f"https://api.lyrics.ovh/v1/{artist_encoded}/{song_encoded}",
            timeout=15
        )

        if response.status_code != 200:
            return {"error": "Song not found. Try a different song."}

        data = response.json()

        if "error" in data:
            return {"error": data["error"]}

        if "lyrics" not in data or not data["lyrics"]:
            return {"error": "No lyrics found for this song."}

        return {
            "title": song.strip(),
            "artist": artist.strip(),
            "lyrics": data["lyrics"],
            "image": None
        }
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Could not fetch lyrics: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


def get_swears():
    """Load swear words from words.txt file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "words.txt")

    swears = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                word = line.strip()
                if word:
                    swears.append(word)
        swears.sort()
    except FileNotFoundError:
        print(f"Warning: words.txt not found at {file_path}")
        swears = []
    return swears


def filter(lyrics, swears):
    """Count occurrences of swear words in lyrics"""
    lyrics_clean = lyrics.translate(str.maketrans('', '', string.punctuation))
    lyrics_words = lyrics_clean.lower().split()

    results = {}
    for swear in swears:
        count = lyrics_words.count(swear.lower())
        if count > 0:
            results[swear] = count

    return results


def yt_url(artist, song):
    """Get YouTube watch URL for the song"""
    try:
        search_query = f"{artist} {song} official"
        yt = YoutubeSearch(search_query, max_results=1).to_json()
        videos = json.loads(yt).get('videos', [])

        if videos:
            song_id = videos[0].get('id')
            if song_id:
                return f"https://www.youtube.com/watch?v={song_id}"
    except Exception as e:
        print(f"YouTube search error: {e}")

    return None
