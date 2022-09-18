#Package import
from re import L
from flask import Flask, render_template, send_file, make_response, url_for, Response, redirect, request 
from Filter import lyric, get_swears, filter,yt_url
#initialise app
def length(thing):
    return len(thing)


app = Flask(__name__)
app.jinja_env.globals.update(len =length)
#decorator for homepage 
@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/result", methods = ['POST','GET'])
def result():
    output = request.form.to_dict()
    song = output["song"]
    song_info = lyric(song)
    video_url = yt_url(song)
    if len(song_info) != 1:
        result = filter(song_info["lyrics"],get_swears())
        return render_template("index.html", result = result, song = song_info, video = video_url)
    else: 
        return render_template("index.html", error = song_info["error"])

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug = True, host = "0.0.0.0",port = 80)




