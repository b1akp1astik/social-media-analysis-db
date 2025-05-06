# app.py
from flask import Flask, request, redirect, render_template
from app.crud import add_media, get_media

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
