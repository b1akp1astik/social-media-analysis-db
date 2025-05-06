# app.py
from flask import Flask, request, redirect, render_template, url_for
from app.crud import add_media, get_media, add_user, get_user, run_query

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

from app.crud import add_project_post, get_project_posts

@app.route("/project-posts", methods=["GET", "POST"])
def project_posts():
    if request.method == "POST":
        proj      = request.form["project"].strip()
        media     = request.form["media"].strip()
        username  = request.form["username"].strip()
        time_post = request.form["time_posted"].strip()

        # Optionally validate time format here…
        add_project_post(proj, media, username, time_post)
        return redirect(f"/project-posts?project={proj}")

    proj   = request.args.get("project", "")
    links  = get_project_posts(proj)
    return render_template(
        "project_posts.html",
        project=proj,
        links=links
    )

from app.crud import add_post_analysis, get_post_analyses

@app.route("/analyses", methods=["GET", "POST"])
def analyses():
    error = None
    if request.method == "POST":
        proj      = request.form["project"].strip()
        field     = request.form["field_name"].strip()
        media     = request.form["media"].strip()
        username  = request.form["username"].strip()
        time_post = request.form["time_posted"].strip()
        value     = request.form["value"].strip()

        if not all([proj, field, media, username, time_post, value]):
            error = "All fields are required."
        else:
            add_post_analysis(proj, field, media, username, time_post, value)
            return redirect(f"/analyses?project={proj}")

    proj     = request.args.get("project", "")
    results  = get_post_analyses(proj)
    return render_template(
        "analyses.html",
        analyses=results,
        project=proj,
        error=error
    )

from app.crud import find_posts, get_project_posts

@app.route("/search-posts", methods=["GET","POST"])
def search_posts():
    criteria = {}
    results = []
    if request.method == "POST":
        # collect form inputs
        criteria = {
            'media':    request.form.get("media","").strip() or None,
            'username': request.form.get("username","").strip() or None,
            'first':    request.form.get("first_name","").strip() or None,
            'last':     request.form.get("last_name","").strip() or None,
            'start':    request.form.get("start_time","").strip() or None,
            'end':      request.form.get("end_time","").strip() or None,
        }
        results = find_posts(**criteria)
        # for each post, also fetch associated projects
        for row in results:
            links = get_project_posts(row["ProjectName"] if "ProjectName" in row else "")
            # Actually, better: query ProjectPost per (media,username,time)
            projs = run_query(
                "SELECT ProjectName FROM ProjectPost "
                "WHERE MediaName=%s AND Username=%s AND TimePosted=%s",
                (row["MediaName"], row["Username"], row["TimePosted"]),
                fetch=True
            )
            row["Projects"] = [r["ProjectName"] for r in projs]
    return render_template("search_posts.html", criteria=criteria, results=results)


if __name__ == "__main__":
    app.run(debug=True)