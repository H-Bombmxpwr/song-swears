import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from Filter import lyric, get_swears, filter, yt_url, search_spotify, get_track_details

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Cache swear words at startup for speed
SWEARS = get_swears()


def length(thing):
    return len(thing)


app.jinja_env.globals.update(len=length)


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/api/autocomplete", methods=['GET'])
def autocomplete():
    """Spotify search autocomplete endpoint"""
    query = request.args.get('q', '').strip()

    if len(query) < 2:
        return jsonify([])

    tracks = search_spotify(query, limit=6)
    return jsonify(tracks)


@app.route("/result", methods=['POST', 'GET'])
def result():
    output = request.form.to_dict()
    track_id = output.get("track_id", "").strip()
    artist = output.get("artist", "").strip()
    song = output.get("song", "").strip()

    # If we have a Spotify track ID, get details from Spotify
    if track_id:
        track_details = get_track_details(track_id)
        if track_details:
            artist = track_details['artist']
            song = track_details['name']
            album_image = track_details['image']
        else:
            album_image = None
    else:
        album_image = None

    if not artist or not song:
        return render_template("index.html", error="Please select a song from the dropdown.")

    # Fetch lyrics
    song_info = lyric(artist, song)

    if "error" in song_info:
        return render_template("index.html", error=song_info["error"])

    # Use Spotify album image if available
    if album_image:
        song_info["image"] = album_image

    # Get YouTube link (not embed)
    video_url = yt_url(artist, song)

    # Filter for swear words
    result = filter(song_info["lyrics"], SWEARS)

    return render_template("index.html", result=result, song=song_info, video=video_url)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
