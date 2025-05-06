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

from datetime import datetime
from flask import Flask, request, redirect, render_template, url_for
from app.crud import add_post, get_posts

@app.route("/posts", methods=["GET", "POST"])
def posts():
    error = None
    media    = ""
    username = ""
    if request.method == "POST":
        media    = request.form["media"].strip()
        username = request.form["username"].strip()
        time_str = request.form["time"].strip()
        text     = request.form["text"].strip()

        # 1) Validate timestamp format
        try:
            # this will raise ValueError on bad format
            datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            error = "Time must be in YYYY-MM-DD HH:MM:SS format."
        else:
            # only insert if valid
            add_post(media, username, time_str, text)
            return redirect(url_for("posts",
                                    media=media,
                                    username=username))

    else:
        # on GET, pre-fill from querystring
        media    = request.args.get("media", "")
        username = request.args.get("username", "")

    # In both the GET case and a POST with error, re-render
    posts = get_posts(media, username)
    return render_template(
        "posts.html",
        posts=posts,
        media=media,
        username=username,
        error=error
    )

from app.crud import add_repost, get_reposts

@app.route("/reposts", methods=["GET", "POST"])
def reposts():
    if request.method == "POST":
        orig_media   = request.form["orig_media"].strip()
        orig_user    = request.form["orig_user"].strip()
        orig_time    = request.form["orig_time"].strip()
        rep_media    = request.form["rep_media"].strip()
        rep_user     = request.form["rep_user"].strip()
        repost_time  = request.form["repost_time"].strip()

        # (Optional: validate timestamps here)
        add_repost(orig_media, orig_user, orig_time,
                   rep_media, rep_user, repost_time)
        return redirect(f"/reposts?orig_media={orig_media}")

    orig_media = request.args.get("orig_media", "")
    reposts    = get_reposts(orig_media)
    return render_template("reposts.html",
                           reposts=reposts,
                           orig_media=orig_media)

from app.crud import add_institute, get_institutes

@app.route("/institutes", methods=["GET", "POST"])
def institutes():
    if request.method == "POST":
        name = request.form["name"].strip()
        if name:
            add_institute(name)
        return redirect("/institutes")

    insts = get_institutes()
    return render_template("institutes.html", institutes=insts)

from app.crud import add_project, get_projects

@app.route("/projects", methods=["GET", "POST"])
def projects():
    if request.method == "POST":
        name      = request.form["name"].strip()
        mgr_first = request.form["mgr_first"].strip()
        mgr_last  = request.form["mgr_last"].strip()
        inst      = request.form["institute"].strip()
        start     = request.form["start_date"].strip()
        end       = request.form["end_date"].strip()
        add_project(name, mgr_first, mgr_last, inst, start, end)
        return redirect("/projects")

    projs = get_projects()
    return render_template("projects.html", projects=projs)

from app.crud import add_field, get_fields

@app.route("/fields", methods=["GET", "POST"])
def fields():
    error = None
    if request.method == "POST":
        proj  = request.form["project"].strip()
        fname = request.form["field_name"].strip()
        if not proj or not fname:
            error = "Both Project and Field name are required."
        else:
            add_field(proj, fname)
            return redirect(f"/fields?project={proj}")

    # on GET or POST-with-error:
    proj   = request.args.get("project", "")
    fields = get_fields(proj)
    return render_template(
        "fields.html",
        fields=fields,
        project=proj,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)