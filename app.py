# app.py
from flask import Flask, request, redirect, render_template, url_for
from app.crud import add_media, get_media, add_user, get_user

app = Flask(__name__)

@app.route("/media", methods=["GET", "POST"])
def media():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            add_media(name)
        return redirect("/media")

    # GET: show form + list
    medias = get_media()
    return render_template("media.html", medias=medias)

@app.route("/")
def home():
    return redirect("/media")

from app.crud import get_user as get_users  # alias existing get_user

@app.route("/users", methods=["GET", "POST"])
def users():
    if request.method == "POST":
        media    = request.form["media"].strip()
        username = request.form["username"].strip()
        first    = request.form["first_name"].strip()
        last     = request.form["last_name"].strip()
        add_user(media, username, first, last)
        return redirect(f"/users?media={media}")

    media = request.args.get("media", "")
    users = get_users(media)
    return render_template("user.html", users=users, media=media)

from app.crud import add_post, get_posts

@app.route("/posts", methods=["GET", "POST"])
def posts():
    if request.method == "POST":
        media    = request.form["media"].strip()
        username = request.form["username"].strip()
        time     = request.form["time"].strip()
        text     = request.form["text"].strip()
        add_post(media, username, time, text)
        return redirect(f"/posts?media={media}&username={username}")

    media    = request.args.get("media", "")
    username = request.args.get("username", "")
    posts    = get_posts(media, username)
    return render_template("posts.html",
                           posts=posts,
                           media=media,
                           username=username)


if __name__ == "__main__":
    app.run(debug=True)