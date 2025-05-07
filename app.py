# app.py
from flask import Flask, request, redirect, render_template, url_for, flash, get_flashed_messages
from app.crud import add_media, get_media, add_user, get_user, run_query, update_media, delete_media
from mysql.connector import IntegrityError, errorcode

app = Flask(__name__)
app.secret_key = "replace_with_a_random_secret"        # needed for flash()

@app.route("/media", methods=["GET","POST"])
def media():
    if request.method=="POST":
        name = request.form.get("name","").strip()
        # 1) Required
        if not name:
            flash("Name cannot be blank.", "danger")
        # 2) Length
        elif len(name) > 50:
            flash("Media name must be 50 characters or fewer.", "danger")
        else:
            # 3) Normalize for case‐insensitive duplicate checks (optional)
            name = name.lower()
            # 4) Try insert
            try:
                add_media(name)
            except IntegrityError as e:
                # see if it’s a duplicate‐key error
                if e.errno == errorcode.ER_DUP_ENTRY:
                    flash(f"“{name}” already exists.", "warning")
                else:
                    flash("Database integrity error.", "danger")
            except Exception as e:
                # log.exception(e)
                flash("Unexpected error when adding media.", "danger")
            else:
                flash(f"Added media: “{name}”", "success")
        return redirect(url_for("media"))

    # GET
    try:
        medias = get_media()
    except Exception:
        flash("Could not load platforms.", "danger")
        medias = []
    return render_template("media.html", medias=medias)


@app.route("/media/edit/<old_name>", methods=["GET","POST"])
def media_edit(old_name):
    new_name = request.form.get("name","").strip()  # ← good, grab this up‐front

    if request.method=="POST":
        # 1) required & length checks
        if not new_name:
            flash("Name cannot be blank.", "danger")
            return redirect(url_for("media_edit", old_name=old_name))
        if len(new_name) > 50:
            flash("Media name must be 50 characters or fewer.", "danger")
            return redirect(url_for("media_edit", old_name=old_name))

        # 2) normalize (if you want case-insensitive)
        norm = new_name.lower()

        # 3) attempt update
        try:
            update_media(old_name, norm)
        except IntegrityError as e:
            # duplicate key?
            if e.errno == errorcode.ER_DUP_ENTRY:
                flash(f"Cannot rename: “{norm}” already exists.", "warning")
            else:
                flash("Database integrity error when renaming.", "danger")
        except Exception as e:
            # log.exception(e)
            flash("Unexpected error renaming media.", "danger")
        else:
            flash(f"Renamed “{old_name}” → “{norm}”.", "success")
            return redirect(url_for("media"))

    # GET (or POST that fell through)
    return render_template("media_edit.html", old_name=old_name)

  
@app.route("/media/delete/<name>", methods=["POST"])
def media_delete(name):
    try:
        delete_media(name)
    except IntegrityError as e:
        # foreign‐key violation?
        if e.errno in (errorcode.ER_ROW_IS_REFERENCED_2, errorcode.ER_ROW_IS_REFERENCED):
            flash(f"Cannot delete “{name}”: other records depend on it.", "warning")
        else:
            flash("Database integrity error when deleting.", "danger")
    except Exception as e:
        # log.exception(e)
        flash("Unexpected error deleting media.", "danger")
    else:
        flash(f"Deleted “{name}”.", "success")
    return redirect(url_for("media"))

@app.route("/")
def home():
    return redirect("/media")

from app.crud import get_user as get_users  # alias existing get_user

@app.route("/users", methods=["GET","POST"])
def users():
    if request.method == "POST":
        media    = request.form.get("media","").strip()
        username = request.form.get("username","").strip()
        first    = request.form.get("first_name","").strip()
        last     = request.form.get("last_name","").strip()
        # optional fields:
        country_birth = request.form.get("country_birth") or None
        country_res   = request.form.get("country_res")   or None

        # AGE: must be integer ≥0 (or blank)
        age_raw = request.form.get("age","").strip()
        if age_raw:
            try:
                age = int(age_raw)
                if age < 0:
                    raise ValueError
            except ValueError:
                flash("Age must be a non-negative integer.", "danger")
                return redirect(url_for("users", media=media))
        else:
            age = None

        # GENDER: if provided, must be one of your ENUM choices
        gender = request.form.get("gender","").strip() or None
        if gender and gender not in ("Male","Female","Other"):
            flash("Gender must be Male, Female, or Other.", "danger")
            return redirect(url_for("users", media=media))

        # VERIFIED checkbox
        is_verified = bool(request.form.get("is_verified"))

        # 1) Required inputs
        if not all([media, username]):
            flash("Media, username are required.", "danger")
            return redirect(url_for("users", media=media))

        # 2) username length
        if len(username) > 40:
            flash("Username must be 40 characters or fewer.", "danger")
            return redirect(url_for("users", media=media))

        # 3) now try to insert
        try:
            add_user(media, username, first, last,
                     country_birth, country_res,
                     age, gender, is_verified)
        except IntegrityError as e:
            # inspect e.errno for more granular messages
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash(f"Cannot add user: platform “{media}” does not exist.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash(f"Username “{username}” already taken on {media}.", "warning")
            else:
                flash("Database integrity error when adding user.", "danger")
        except Exception:
            flash("Unexpected error adding user.", "danger")
        else:
            flash(f"Added user {username}@{media}.", "success")

        return redirect(url_for("users", media=media))

    # GET: list users (optionally filtered)
    media = request.args.get("media","").strip()
    users = get_users(media) if media else []
    return render_template("user.html", users=users, media=media)

from datetime import datetime
from flask import Flask, request, redirect, render_template, url_for, flash
from mysql.connector import IntegrityError, errorcode
from app.crud import add_post, get_posts

from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from mysql.connector import IntegrityError, errorcode
from app.crud import add_post, get_posts

@app.route("/posts", methods=["GET", "POST"])
def posts():
    # on each render
    media    = request.args.get("media", "").strip()
    username = request.args.get("username", "").strip()

    if request.method == "POST":
        # 1) pull & strip inputs
        media      = request.form.get("media","").strip()
        username   = request.form.get("username","").strip()
        time_str   = request.form.get("time","").strip()
        text       = request.form.get("text","").strip()

        # optional metadata
        city       = request.form.get("city") or None
        state      = request.form.get("state") or None
        country    = request.form.get("country") or None

        # likes/dislikes must be integers ≥ 0
        likes_raw    = request.form.get("likes","").strip()
        dislikes_raw = request.form.get("dislikes","").strip()
        try:
            likes    = int(likes_raw)    if likes_raw    else 0
            dislikes = int(dislikes_raw) if dislikes_raw else 0
            if likes < 0 or dislikes < 0:
                raise ValueError
        except ValueError:
            flash("Likes/dislikes must be non-negative integers.", "danger")
            return redirect(url_for("posts", media=media, username=username))

        # multimedia flag
        has_multimedia = bool(request.form.get("has_multimedia"))

        # 2) required fields
        if not all([media, username, time_str, text]):
            flash("Media, username, time and text are all required.", "danger")
            return redirect(url_for("posts", media=media, username=username))

        # 3) timestamp format: accept both with and without seconds
        try:
            # first try full precision
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # try without seconds
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            except ValueError:
                flash("Time must be in YYYY-MM-DD HH:MM[:SS] format.", "danger")
                return redirect(url_for("posts", media=media, username=username))
            else:
                # add seconds = 0
                dt = dt.replace(second=0)

        # now normalize to full‐precision string
        normalized_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        # 4) insert
        try:
            add_post(
                media, username, normalized_time, text,
                city, state, country,
                likes, dislikes, has_multimedia
            )
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash("Cannot add post: user or media does not exist.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash("This post (same user, media, and timestamp) already exists.", "warning")
            else:
                flash("Database integrity error adding post.", "danger")
        except Exception:
            flash("Unexpected error adding post.", "danger")
        else:
            flash("Post added successfully!", "success")
            return redirect(url_for("posts",
                                    media=media,
                                    username=username))

    # GET (or after a validation failure): show form + existing posts
    posts = get_posts(media, username)
    return render_template(
        "posts.html",
        posts=posts,
        media=media,
        username=username
    )

from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from mysql.connector import IntegrityError, errorcode
from app.crud import add_repost, get_reposts


def _normalize_timestamp(ts: str, label: str) -> str:
    """
    Try parsing ts with seconds or without; return a string
    formatted as 'YYYY-MM-DD HH:MM:SS', or raise ValueError.
    """
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            dt = datetime.strptime(ts, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    raise ValueError(f"{label} must be in YYYY-MM-DD HH:MM[:SS] format.")

@app.route("/reposts", methods=["GET", "POST"])
def reposts():
    if request.method == "POST":
        # 1) pull & strip inputs
        orig_media  = request.form.get("orig_media","").strip()
        orig_user   = request.form.get("orig_user","").strip()
        orig_time   = request.form.get("orig_time","").strip()
        rep_media   = request.form.get("rep_media","").strip()
        rep_user    = request.form.get("rep_user","").strip()
        repost_time = request.form.get("repost_time","").strip()

        # 2) required fields
        if not all([orig_media, orig_user, orig_time, rep_media, rep_user, repost_time]):
            flash("All repost fields are required.", "danger")
            return redirect(url_for("reposts", orig_media=orig_media))

        # 3) normalize timestamps (accept with or without seconds)
        try:
            orig_time   = _normalize_timestamp(orig_time, "Original time")
            repost_time = _normalize_timestamp(repost_time, "Repost time")
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("reposts", orig_media=orig_media))

        # 4) attempt insert
        try:
            add_repost(orig_media, orig_user, orig_time,
                       rep_media, rep_user, repost_time)
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash("Cannot add repost: original post or user/media not found.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash("This repost already exists.", "warning")
            else:
                flash("Database integrity error adding repost.", "danger")
        except Exception:
            flash("Unexpected error adding repost.", "danger")
        else:
            flash("Repost recorded successfully!", "success")
            return redirect(url_for("reposts", orig_media=orig_media))

    # GET (or after failure): show list & form
    orig_media = request.args.get("orig_media", "").strip()
    reposts    = get_reposts(orig_media or None)
    return render_template(
        "reposts.html",
        reposts=reposts,
        orig_media=orig_media
    )

from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from mysql.connector import IntegrityError, errorcode
from app.crud import add_institute, get_institutes, add_project, get_projects

@app.route("/institutes", methods=["GET", "POST"])
def institutes():
    if request.method == "POST":
        name = request.form.get("name", "").strip()

        # 1) Required
        if not name:
            flash("Institute name cannot be blank.", "danger")
            return redirect(url_for("institutes"))

        # 2) Insert & catch duplicates
        try:
            add_institute(name)
        except IntegrityError as e:
            if e.errno == errorcode.ER_DUP_ENTRY:
                flash(f"Institute “{name}” already exists.", "warning")
            else:
                flash("Database error adding institute.", "danger")
        except Exception:
            flash("Unexpected error adding institute.", "danger")
        else:
            flash(f"Added institute: “{name}”", "success")

        return redirect(url_for("institutes"))

    # GET: render list
    insts = get_institutes()
    return render_template("institutes.html", institutes=insts)


@app.route("/projects", methods=["GET", "POST"])
def projects():
    if request.method == "POST":
        # 1) Pull & strip
        name      = request.form.get("name", "").strip()
        mgr_first = request.form.get("mgr_first", "").strip()
        mgr_last  = request.form.get("mgr_last", "").strip()
        inst      = request.form.get("institute", "").strip()
        start_str = request.form.get("start_date", "").strip()
        end_str   = request.form.get("end_date", "").strip()

        # 2) Required fields
        if not all([name, mgr_first, mgr_last, inst, start_str, end_str]):
            flash("All project fields are required.", "danger")
            return redirect(url_for("projects"))

        # 3) Validate dates
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d").date()
            end   = datetime.strptime(end_str,   "%Y-%m-%d").date()
        except ValueError:
            flash("Start/End dates must be YYYY-MM-DD.", "danger")
            return redirect(url_for("projects"))

        # 4) Logical check: end ≥ start
        if end < start:
            flash("End date cannot be before start date.", "warning")
            return redirect(url_for("projects"))

        # 5) Insert & catch IntegrityErrors
        try:
            add_project(name, mgr_first, mgr_last, inst, start_str, end_str)
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash(f"Institute “{inst}” does not exist.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash(f"Project “{name}” already exists.", "warning")
            else:
                flash("Database error adding project.", "danger")
        except Exception:
            flash("Unexpected error adding project.", "danger")
        else:
            flash(f"Added project: “{name}” (Mgr: {mgr_first} {mgr_last})", "success")

        return redirect(url_for("projects"))

    # GET: show all projects
    projs = get_projects()
    return render_template("projects.html", projects=projs)
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from mysql.connector import IntegrityError, errorcode
from app.crud import add_field, get_fields, add_project_post, get_project_posts

@app.route("/fields", methods=["GET", "POST"])
def fields():
    if request.method == "POST":
        proj  = request.form.get("project", "").strip()
        fname = request.form.get("field_name", "").strip()

        # 1) Required
        if not proj or not fname:
            flash("Both Project and Field name are required.", "danger")
            return redirect(url_for("fields", project=proj))

        # 2) Insert & catch FK / duplicates
        try:
            add_field(proj, fname)
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash(f"Project “{proj}” does not exist.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash(f"Field “{fname}” already exists in project “{proj}”.", "warning")
            else:
                flash("Database error adding field.", "danger")
        except Exception:
            flash("Unexpected error adding field.", "danger")
        else:
            flash(f"Added field “{fname}” to project “{proj}”.", "success")

        return redirect(url_for("fields", project=proj))

    # GET: list fields for optional project
    proj   = request.args.get("project", "").strip()
    fields = get_fields(proj)
    return render_template(
        "fields.html",
        fields=fields,
        project=proj
    )


@app.route("/project-posts", methods=["GET", "POST"])
def project_posts():
    if request.method == "POST":
        proj      = request.form.get("project", "").strip()
        media     = request.form.get("media", "").strip()
        username  = request.form.get("username", "").strip()
        time_post = request.form.get("time_posted", "").strip()

        # 1) Required
        if not all([proj, media, username, time_post]):
            flash("Project, Media, Username & TimePosted are required.", "danger")
            return redirect(url_for("project_posts", project=proj))

        # 2) Validate timestamp
        try:
            datetime.strptime(time_post, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            flash("TimePosted must be YYYY-MM-DD HH:MM:SS.", "warning")
            return redirect(url_for("project_posts", project=proj))

        # 3) Insert & catch errors
        try:
            add_project_post(proj, media, username, time_post)
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash("Project, media, user or post does not exist.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash("This post is already linked to that project.", "warning")
            else:
                flash("Database error linking project to post.", "danger")
        except Exception:
            flash("Unexpected error linking post to project.", "danger")
        else:
            flash(f"Linked post [{media}/{username} @ {time_post}] to project “{proj}”.", "success")

        return redirect(url_for("project_posts", project=proj))

    # GET: list links for optional project
    proj  = request.args.get("project", "").strip()
    links = get_project_posts(proj)
    return render_template(
        "project_posts.html",
        project=proj,
        links=links
    )

from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from mysql.connector import IntegrityError, errorcode
from app.crud import add_post_analysis, get_post_analyses

@app.route("/analyses", methods=["GET", "POST"])
def analyses():
    if request.method == "POST":
        proj      = request.form.get("project","").strip()
        field     = request.form.get("field_name","").strip()
        media     = request.form.get("media","").strip()
        username  = request.form.get("username","").strip()
        time_post = request.form.get("time_posted","").strip()
        value     = request.form.get("value","").strip()

        # 1) All required
        if not all([proj, field, media, username, time_post, value]):
            flash("All fields are required.", "danger")
            return redirect(url_for("analyses", project=proj))

        # 2) Timestamp format
        try:
            datetime.strptime(time_post, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            flash("TimePosted must be YYYY-MM-DD HH:MM:SS.", "warning")
            return redirect(url_for("analyses", project=proj))

        # 3) Insert & catch
        try:
            add_post_analysis(proj, field, media, username, time_post, value)
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash("Project, field, media, user or post does not exist.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash("This analysis value is already recorded.", "warning")
            else:
                flash("Database error recording analysis.", "danger")
        except Exception:
            flash("Unexpected error recording analysis.", "danger")
        else:
            flash(f"Recorded analysis “{field}={value}” for {media}/{username}@{time_post} under project “{proj}”.", "success")

        return redirect(url_for("analyses", project=proj))

    # GET: show existing analyses for optional project
    proj     = request.args.get("project","").strip()
    results  = get_post_analyses(proj)
    return render_template(
        "analyses.html",
        analyses=results,
        project=proj
    )
from datetime import datetime
from flask import flash, redirect, render_template, request, url_for
from mysql.connector import IntegrityError, errorcode
from app.crud import find_posts, get_project_posts, get_experiment_results, get_fields

@app.route("/search-posts", methods=["GET", "POST"])
def search_posts():
    criteria = {}
    results = []
    if request.method == "POST":
        # 1) Gather + normalize inputs
        media    = request.form.get("media","").strip() or None
        username = request.form.get("username","").strip() or None
        first    = request.form.get("first_name","").strip() or None
        last     = request.form.get("last_name","").strip() or None
        start    = request.form.get("start_time","").strip() or None
        end      = request.form.get("end_time","").strip() or None

        criteria = dict(media=media, username=username,
                        first=first, last=last,
                        start=start, end=end)

        # 2) Require at least one criterion
        if not any(criteria.values()):
            flash("Please specify at least one search criterion.", "warning")
            return redirect(url_for("search_posts"))

        # 3) Validate timestamps if provided
        for label, ts in (("Start", start), ("End", end)):
            if ts:
                try:
                    datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    flash(f"{label} time must be YYYY-MM-DD HH:MM:SS.", "danger")
                    return redirect(url_for("search_posts"))

        # 4) Run query + attach projects
        try:
            results = find_posts(**criteria)
            for row in results:
                projs = get_project_posts(None)  # drop unused code
                projs = run_query(
                    "SELECT ProjectName FROM ProjectPost "
                    "WHERE MediaName=%s AND Username=%s AND TimePosted=%s",
                    (row["MediaName"], row["Username"], row["TimePosted"]),
                    fetch=True
                )
                row["Projects"] = [r["ProjectName"] for r in projs]
        except Exception:
            flash("Unexpected error searching posts.", "danger")
            results = []

        # 5) Feedback on 0 results
        if not results:
            flash("No posts found matching those criteria.", "info")

    return render_template(
        "search_posts.html",
        criteria=criteria,
        results=results
    )


@app.route("/search-experiments", methods=["GET", "POST"])
def search_experiments():
    project     = ""
    results     = []
    percentages = {}

    if request.method == "POST":
        project = request.form.get("project","").strip()
        if not project:
            flash("Project name is required.", "danger")
            return redirect(url_for("search_experiments"))

        # 1) Fetch experiment results
        try:
            results = get_experiment_results(project)
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash(f"Project “{project}” does not exist.", "warning")
            else:
                flash("Database error retrieving experiment.", "danger")
            results = []
        except Exception:
            flash("Unexpected error retrieving experiment.", "danger")
            results = []

        # 2) Feedback on empty
        if not results:
            flash(f"No posts linked to project “{project}”.", "info")
        else:
            # 3) Compute coverage
            field_list = [f["FieldName"] for f in get_fields(project)]
            unique_posts = {
                (r["MediaName"], r["Username"], r["TimePosted"])
                for r in results
            }
            total = len(unique_posts)
            for fld in field_list:
                count = sum(
                    1 for r in results
                    if r["FieldName"] == fld and r["Value"] is not None
                )
                percentages[fld] = f"{(count/total*100):.1f}%" if total else "0%"

    return render_template(
        "search_experiments.html",
        project=project,
        results=results,
        percentages=percentages
    )

if __name__ == "__main__":
    app.run(debug=True)