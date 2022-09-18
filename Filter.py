import requests
from contextlib import suppress
import string
from youtube_search import YoutubeSearch
import json

def lyric(song):
    json = requests.get(f"https://some-random-api.ml/lyrics?title={song}").json()

        

    with suppress(KeyError):
            if json["error"]:
                return {"error": json["error"]}

    return {"title": str(json["title"]), "artist": str(json["author"]), "lyrics": json["lyrics"], "image": json["thumbnail"]["genius"] }


def get_swears():
    file = open("/Users/hunte/Documents/Python/BadFilter/words.txt", 'r')
    swears = []
    for line in file:
        line = line.split("\n")[0]
        swears.append(line)
    swears.sort()
    file.close()
    return swears

def filter(lyrics,swears):
    lyrics = lyrics.translate(str.maketrans('', '', string.punctuation)) #remove the puncuation from the lyrics
    lyrics = str(lyrics).lower().split()
    results = {}
    for i in swears:
        results[i] = lyrics.count(i)
    results = {k: v for k, v in results.items() if v}

    return results

def yt_url(song):
    info = lyric(song)
    if len(info) == 1:
        return
    song = str(info["title"]) + " " + str(info["artist"])
    yt = YoutubeSearch(str(song), max_results=1).to_json()
    try:
        song_id = str(json.loads(yt)['videos'][0]['id'])
        url = "https://www.youtube.com/embed/" + song_id + "?autoplay=1"
        if url == None:
            return "song not found"
    except:
        return None
    return url







