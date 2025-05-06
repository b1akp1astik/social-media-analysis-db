# app.py
from flask import Flask, request, redirect, render_template, url_for
from app.crud import add_media, get_media, add_user, get_users

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

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/users", methods=["GET", "POST"])
def users():
    if request.method == "POST":
        # pull form values
        media   = request.form["media"]
        user    = request.form["username"]
        first   = request.form["first_name"]
        last    = request.form["last_name"]
        # optional fields left out for now…
        add_user(media, user, first, last)
        return redirect(url_for("users"))

    # on GET, fetch and display
    media = request.args.get("media", "") 
    users = get_users(media)  # list of dicts with FirstName, LastName, etc.
    return render_template("user.html", users=users, media=media)