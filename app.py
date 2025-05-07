# app.py
from flask import (
    Flask,
    request,
    redirect,
    render_template,
    url_for,
    flash,
    get_flashed_messages
)
from mysql.connector import IntegrityError, errorcode
from datetime import datetime

from app.crud import (
    # Media
    add_media, get_media, update_media, delete_media,
    # Users
    add_user, get_user as get_users, update_user, delete_user,
    # Posts
    add_post, get_posts, update_post, delete_post,
    # Reposts
    add_repost, get_reposts, update_repost, delete_repost,
    # Institutes
    add_institute, get_institutes, update_institute, delete_institute,
    # Projects
    add_project, get_projects, update_project, delete_project, get_project,
    # Fields
    add_field, get_fields, update_field, delete_field, get_field,
    # Project ↔ Post links
    add_project_post, get_project_posts, update_project_post, delete_project_post, get_project_post,
    # Analyses
    add_post_analysis, get_post_analyses, update_post_analysis, delete_post_analysis,
    # Searches
    find_posts, get_experiment_results,
    # Misc
    run_query
)

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

# ——— List & Create Users ———
@app.route("/users", methods=["GET", "POST"])
def users():
    # always load the full list of media platforms for the dropdown
    all_medias = [row["MediaName"] for row in get_media()]

    # which media are we currently filtering by?
    media = request.args.get("media", "").strip()

    if request.method == "POST":
        # pull & strip inputs
        media    = request.form.get("media", "").strip()
        username = request.form.get("username", "").strip()
        first    = request.form.get("first_name", "").strip() or None
        last     = request.form.get("last_name", "").strip() or None

        # optional fields
        country_birth = request.form.get("country_birth") or None
        country_res   = request.form.get("country_res")   or None

        # age must be a non-negative integer if provided
        age_raw = request.form.get("age", "").strip()
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

        # gender must be one of your ENUMs
        gender = request.form.get("gender", "").strip() or None
        if gender and gender not in ("Male", "Female", "Other"):
            flash("Gender must be Male, Female, or Other.", "danger")
            return redirect(url_for("users", media=media))

        is_verified = bool(request.form.get("is_verified"))

        # required: media & username
        if not media or not username:
            flash("Media and username are required.", "danger")
            return redirect(url_for("users", media=media))

        # username length
        if len(username) > 40:
            flash("Username must be 40 characters or fewer.", "danger")
            return redirect(url_for("users", media=media))

        # attempt insert
        try:
            add_user(media, username, first, last,
                     country_birth, country_res,
                     age, gender, is_verified)
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash(f"Platform “{media}” does not exist.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash(f"Username “{username}” already taken on {media}.", "warning")
            else:
                flash("Database integrity error when adding user.", "danger")
        except Exception:
            flash("Unexpected error adding user.", "danger")
        else:
            flash(f"Added user {username}@{media}.", "success")

        return redirect(url_for("users", media=media))

    # GET: fetch and render
    if media:
        users = get_users(media)
    else:
        # no filter → show every user
        users = run_query("SELECT * FROM User", fetch=True)

    return render_template("user.html",
                           users=users,
                           media=media,
                           all_medias=all_medias)


# ——— Edit User ———
@app.route("/users/edit/<media>/<username>", methods=["GET", "POST"])
def user_edit(media, username):
    # load the record for GET
    existing = get_users(media, username)
    user = existing[0] if existing else {}

    # pull new values on POST
    new_first        = request.form.get("first_name", "").strip() or None
    new_last         = request.form.get("last_name", "").strip() or None
    new_country_birth = request.form.get("country_birth") or None
    new_country_res   = request.form.get("country_res")   or None
    age_raw           = request.form.get("age", "").strip()
    gender            = request.form.get("gender", "").strip() or None
    is_verified       = bool(request.form.get("is_verified"))

    if request.method == "POST":
        # validate age
        if age_raw:
            try:
                new_age = int(age_raw)
                if new_age < 0:
                    raise ValueError
            except ValueError:
                flash("Age must be a non-negative integer.", "danger")
                return redirect(url_for("user_edit", media=media, username=username))
        else:
            new_age = None

        # validate gender
        if gender and gender not in ("Male", "Female", "Other"):
            flash("Gender must be Male, Female, or Other.", "danger")
            return redirect(url_for("user_edit", media=media, username=username))

        # attempt update
        try:
            update_user(
                media, username,
                FirstName=new_first,
                LastName=new_last,
                CountryOfBirth=new_country_birth,
                CountryOfResidence=new_country_res,
                Age=new_age,
                Gender=gender,
                IsVerified=is_verified
            )
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash(f"Platform “{media}” does not exist.", "warning")
            else:
                flash("Database integrity error when updating user.", "danger")
        except Exception:
            flash("Unexpected error updating user.", "danger")
        else:
            flash(f"Updated user {username}@{media}.", "success")
            return redirect(url_for("users", media=media))

    return render_template("user_edit.html",
                           media=media,
                           user=user)


# ——— Delete User ———
@app.route("/users/delete/<media>/<username>", methods=["POST"])
def user_delete(media, username):
    try:
        delete_user(media, username)
    except IntegrityError as e:
        if e.errno in (errorcode.ER_ROW_IS_REFERENCED_2, errorcode.ER_ROW_IS_REFERENCED):
            flash("Cannot delete user: related posts or reposts exist.", "warning")
        else:
            flash("Database integrity error when deleting user.", "danger")
    except Exception:
        flash("Unexpected error deleting user.", "danger")
    else:
        flash(f"Deleted user {username}@{media}.", "success")
    return redirect(url_for("users", media=media))

@app.route("/posts", methods=["GET", "POST"])
def posts():
    # For filter dropdowns
    all_medias = [m["MediaName"] for m in get_media()]
    media      = request.args.get("media", "").strip()
    all_users  = get_users(media) if media else []
    username   = request.args.get("username", "").strip()

    if request.method=="POST":
        # Pull & strip inputs
        media      = request.form.get("media","").strip()
        username   = request.form.get("username","").strip()
        time_str   = request.form.get("time","").strip()
        text       = request.form.get("text","").strip()
        city       = request.form.get("city") or None
        state      = request.form.get("state") or None
        country    = request.form.get("country") or None

        # Validate engagement
        try:
            likes    = int(request.form.get("likes","")   or 0)
            dislikes = int(request.form.get("dislikes","") or 0)
            if likes<0 or dislikes<0:
                raise ValueError
        except ValueError:
            flash("Likes/dislikes must be non-negative integers.", "danger")
            return redirect(url_for("posts", media=media, username=username))

        has_multimedia = bool(request.form.get("has_multimedia"))

        # Required fields
        if not all([media, username, time_str, text]):
            flash("Media, username, time and text are required.", "danger")
            return redirect(url_for("posts", media=media, username=username))

        # Parse timestamp (with or without seconds)
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                dt = dt.replace(second=0)
            except ValueError:
                flash("Time must be YYYY-MM-DD HH:MM[:SS].", "danger")
                return redirect(url_for("posts", media=media, username=username))
        normalized_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        # Insert
        try:
            add_post(media, username, normalized_time, text,
                     city, state, country,
                     likes, dislikes, has_multimedia)
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash("Cannot add post: user or media does not exist.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash("This post already exists.", "warning")
            else:
                flash("Database integrity error adding post.", "danger")
        except Exception:
            flash("Unexpected error adding post.", "danger")
        else:
            flash("Post added successfully!", "success")
            return redirect(url_for("posts", media=media, username=username))

    # GET: fetch and render
    posts = get_posts(media or None, username or None)
    return render_template(
        "posts.html",
        all_medias=all_medias,
        all_users=all_users,
        posts=posts,
        media=media,
        username=username
    )

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

@app.route("/posts/edit/<media>/<username>/<path:time_posted>", methods=["GET", "POST"])
def post_edit(media, username, time_posted):
    # 1) normalize the incoming URL component
    try:
        norm_key = _normalize_timestamp(time_posted, "TimePosted")
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("posts", media=media, username=username))

    # 2) fetch all posts for this user/media and find the one matching our key
    rows = get_posts(media, username)
    post = None
    for p in rows:
        # p["TimePosted"] might be a datetime; convert to string
        ts = p["TimePosted"]
        # if it's not already a string, format it
        if not isinstance(ts, str):
            ts = ts.strftime("%Y-%m-%d %H:%M:%S")
        if ts == norm_key:
            post = p
            break

    if not post:
        flash("Post not found.", "warning")
        return redirect(url_for("posts", media=media, username=username))

    if request.method == "POST":
        # pull & normalize again for updates
        raw_time = request.form.get("time", "").strip()
        text     = request.form.get("text", "").strip()
        city     = request.form.get("city") or None
        state    = request.form.get("state") or None
        country  = request.form.get("country") or None

        # validate likes/dislikes
        likes_raw    = request.form.get("likes", "").strip()
        dislikes_raw = request.form.get("dislikes", "").strip()
        try:
            likes    = int(likes_raw)    if likes_raw    else 0
            dislikes = int(dislikes_raw) if dislikes_raw else 0
            if likes < 0 or dislikes < 0:
                raise ValueError
        except ValueError:
            flash("Likes/dislikes must be non-negative integers.", "danger")
            return redirect(url_for("post_edit",
                                    media=media,
                                    username=username,
                                    time_posted=time_posted))

        has_multimedia = bool(request.form.get("has_multimedia"))

        if not all([raw_time, text]):
            flash("Time and text are required.", "danger")
            return redirect(url_for("post_edit",
                                    media=media,
                                    username=username,
                                    time_posted=time_posted))

        try:
            normalized_time = _normalize_timestamp(raw_time, "Time")
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("post_edit",
                                    media=media,
                                    username=username,
                                    time_posted=time_posted))

        # attempt update (note: updating TimePosted will change the PK)
        try:
            update_post(
                media, username, norm_key,
                TimePosted=normalized_time,
                TextContent=text,
                City=city,
                State=state,
                Country=country,
                Likes=likes,
                Dislikes=dislikes,
                HasMultimedia=has_multimedia
            )
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash("Cannot update post: user or media doesn’t exist.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash("Another post already exists at that timestamp.", "warning")
            else:
                flash("Database integrity error updating post.", "danger")
        except Exception:
            flash("Unexpected error updating post.", "danger")
        else:
            flash("Post updated successfully!", "success")
            return redirect(url_for("posts",
                                    media=media,
                                    username=username))

    # on GET (or if validation failed), render the form with the post’s current values
    return render_template("posts_edit.html", post=post)

# ——— Delete Post ———
@app.route("/posts/delete/<media>/<username>/<time_posted>", methods=["POST"])
def post_delete(media, username, time_posted):
    try:
        delete_post(media, username, time_posted)
    except IntegrityError as e:
        if e.errno in (errorcode.ER_ROW_IS_REFERENCED_2, errorcode.ER_ROW_IS_REFERENCED):
            flash("Cannot delete: related records exist.", "warning")
        else:
            flash("Database integrity error when deleting post.", "danger")
    except Exception:
        flash("Unexpected error deleting post.", "danger")
    else:
        flash("Post deleted.", "success")
    return redirect(url_for("posts", media=media, username=username))

def _normalize_timestamp(ts: str, label: str) -> str:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(ts, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    raise ValueError(f"{label} must be in YYYY-MM-DD HH:MM[:SS] format.")

# ——— List & Create Reposts ———
@app.route("/reposts", methods=["GET", "POST"])
def reposts():
    all_medias = [m["MediaName"] for m in get_media()]
    orig_media = request.args.get("orig_media", "").strip()

    if request.method == "POST":
        om, ou, ot, rm, ru, rt = (
            request.form.get(f, "").strip()
            for f in ("orig_media","orig_user","orig_time",
                      "rep_media","rep_user","repost_time")
        )

        if not all([om, ou, ot, rm, ru, rt]):
            flash("All repost fields are required.", "danger")
            return redirect(url_for("reposts", orig_media=om))

        try:
            ot = _normalize_timestamp(ot, "Original time")
            rt = _normalize_timestamp(rt, "Repost time")
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("reposts", orig_media=om))

        try:
            add_repost(om, ou, ot, rm, ru, rt)
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash("Original post or user/media not found.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash("This repost already exists.", "warning")
            else:
                flash("Database integrity error adding repost.", "danger")
        else:
            flash("Repost recorded successfully!", "success")
            return redirect(url_for("reposts", orig_media=om))

    reposts = get_reposts(orig_media or None)
    return render_template(
        "reposts.html",
        all_medias=all_medias,
        reposts=reposts,
        orig_media=orig_media
    )


# ——— Edit Repost ———
@app.route(
  "/reposts/edit/"
  "<orig_media>/<orig_user>/<path:orig_time>/"
  "<rep_media>/<rep_user>/<path:repost_time>",
  methods=["GET","POST"]
)
def repost_edit(orig_media, orig_user, orig_time, rep_media, rep_user, repost_time):
    rows = get_reposts(orig_media) or []
    repost = next((
        r for r in rows
        if str(r["OrigMedia"])     == orig_media
        and str(r["OrigUser"])     == orig_user
        and str(r["OrigTime"])     == orig_time
        and str(r["ReposterMedia"])== rep_media
        and str(r["ReposterUser"]) == rep_user
        and str(r["RepostTime"])   == repost_time
    ), None)

    if not repost:
        flash("Repost not found.", "warning")
        return redirect(url_for("reposts", orig_media=orig_media))

    if request.method == "POST":
        new_vals = {k: request.form.get(k, "").strip() for k in
                    ("orig_media","orig_user","orig_time",
                     "rep_media","rep_user","repost_time")}
        if not all(new_vals.values()):
            flash("All fields are required.", "danger")
            return redirect(request.url)

        try:
            new_vals["orig_time"]  = _normalize_timestamp(new_vals["orig_time"],  "Original time")
            new_vals["repost_time"]= _normalize_timestamp(new_vals["repost_time"],"Repost time")
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(request.url)

        try:
            update_repost(
                orig_media, orig_user, orig_time, repost_time,
                OrigMedia=new_vals["orig_media"],
                OrigUser=new_vals["orig_user"],
                OrigTime=new_vals["orig_time"],
                ReposterMedia=new_vals["rep_media"],
                ReposterUser=new_vals["rep_user"],
                RepostTime=new_vals["repost_time"],
            )
        except IntegrityError:
            flash("Database integrity error updating repost.", "danger")
        else:
            flash("Repost updated successfully!", "success")
            return redirect(url_for("reposts", orig_media=new_vals["orig_media"]))

    return render_template("repost_edit.html", repost=repost)


# ——— Delete Repost ———
@app.route(
    "/reposts/delete/"
    "<orig_media>/<orig_user>/<path:orig_time>/"
    "<rep_media>/<rep_user>/<path:repost_time>",
    methods=["POST"]
)
def repost_delete(orig_media, orig_user, orig_time, rep_media, rep_user, repost_time):
    try:
        delete_repost(orig_media, orig_user, orig_time, rep_media, rep_user, repost_time)
    except IntegrityError:
        flash("Cannot delete repost: related records exist.", "warning")
    else:
        flash("Repost deleted.", "success")
    return redirect(url_for("reposts", orig_media=orig_media))

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


# ——— Edit Institute ———
@app.route("/institutes/edit/<old_name>", methods=["GET", "POST"])
def institutes_edit(old_name):
    new_name = request.form.get("name", "").strip()

    if request.method == "POST":
        # 1) Required & length
        if not new_name:
            flash("Institute name cannot be blank.", "danger")
            return redirect(url_for("institutes_edit", old_name=old_name))
        if len(new_name) > 100:
            flash("Institute name must be 100 characters or fewer.", "danger")
            return redirect(url_for("institutes_edit", old_name=old_name))

        # 2) Attempt update
        try:
            update_institute(old_name, new_name)
        except IntegrityError as e:
            if e.errno == errorcode.ER_DUP_ENTRY:
                flash(f"Cannot rename: “{new_name}” already exists.", "warning")
            else:
                flash("Database integrity error when renaming institute.", "danger")
        except Exception:
            flash("Unexpected error renaming institute.", "danger")
        else:
            flash(f"Renamed institute “{old_name}” → “{new_name}”.", "success")
            return redirect(url_for("institutes"))

    # GET (or POST fell through)
    return render_template("institutes_edit.html", old_name=old_name)


# ——— Delete Institute ———
@app.route("/institutes/delete/<name>", methods=["POST"])
def institutes_delete(name):
    try:
        delete_institute(name)
    except IntegrityError as e:
        # FK violation?
        if e.errno in (errorcode.ER_ROW_IS_REFERENCED_2, errorcode.ER_ROW_IS_REFERENCED):
            flash(f"Cannot delete institute “{name}”: other records depend on it.", "warning")
        else:
            flash("Database integrity error when deleting institute.", "danger")
    except Exception:
        flash("Unexpected error deleting institute.", "danger")
    else:
        flash(f"Deleted institute “{name}”.", "success")

    return redirect(url_for("institutes"))

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

# ——— Edit Project ———
@app.route("/projects/edit/<project_name>", methods=["GET", "POST"])
def projects_edit(project_name):
    # fetch existing to pre-fill (optional)
    existing = get_project(project_name)
    proj = existing[0] if existing else {}

    if request.method == "POST":
        # pull & strip
        new_name   = request.form.get("name",      "").strip()
        mgr_first  = request.form.get("mgr_first", "").strip()
        mgr_last   = request.form.get("mgr_last",  "").strip()
        inst       = request.form.get("institute", "").strip()
        start_str  = request.form.get("start_date","").strip()
        end_str    = request.form.get("end_date",  "").strip()

        # 1) all required
        if not all([new_name, mgr_first, mgr_last, inst, start_str, end_str]):
            flash("All project fields are required.", "danger")
            return redirect(url_for("projects_edit", project_name=project_name))

        # 2) validate dates
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d").date()
            end   = datetime.strptime(end_str,   "%Y-%m-%d").date()
        except ValueError:
            flash("Dates must be YYYY-MM-DD.", "danger")
            return redirect(url_for("projects_edit", project_name=project_name))

        # 3) logical check
        if end < start:
            flash("End date cannot be before start date.", "warning")
            return redirect(url_for("projects_edit", project_name=project_name))

        # 4) attempt update (note: if you allow renaming the PK you pass old name)
        try:
            update_project(
                project_name,
                ProjectName=new_name,
                ManagerFirstName=mgr_first,
                ManagerLastName=mgr_last,
                InstituteName=inst,
                StartDate=start_str,
                EndDate=end_str
            )
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash(f"Institute “{inst}” does not exist.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash(f"Project name “{new_name}” already in use.", "warning")
            else:
                flash("Database integrity error when updating project.", "danger")
        except Exception:
            flash("Unexpected error updating project.", "danger")
        else:
            flash(f"Updated project “{project_name}”.", "success")
            return redirect(url_for("projects"))

    # GET (or fall-through)
    return render_template("projects_edit.html", project=proj)


# ——— Delete Project ———
@app.route("/projects/delete/<project_name>", methods=["POST"])
def projects_delete(project_name):
    try:
        delete_project(project_name)
    except IntegrityError as e:
        if e.errno in (errorcode.ER_ROW_IS_REFERENCED_2, errorcode.ER_ROW_IS_REFERENCED):
            flash(f"Cannot delete project “{project_name}”: dependent records exist.", "warning")
        else:
            flash("Database integrity error when deleting project.", "danger")
    except Exception:
        flash("Unexpected error deleting project.", "danger")
    else:
        flash(f"Deleted project “{project_name}”.", "success")
    return redirect(url_for("projects"))

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

# ——— Edit Field ———
@app.route("/fields/edit/<project>/<field_name>", methods=["GET","POST"])
def fields_edit(project, field_name):
    # 1) load current value
    existing = get_field(project)
    field = next((f for f in existing if f["FieldName"] == field_name), None)
    if not field:
        flash(f"Field “{field_name}” not found in project “{project}”.", "warning")
        return redirect(url_for("fields", project=project))

    if request.method == "POST":
        new_name = request.form.get("field_name","").strip()
        if not new_name:
            flash("Field name cannot be blank.", "danger")
            return redirect(url_for("fields_edit", project=project, field_name=field_name))
        try:
            update_field(project, field_name, new_name)
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash(f"Project “{project}” does not exist.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash(f"Field “{new_name}” already exists in project “{project}”.", "warning")
            else:
                flash("Database error updating field.", "danger")
        except Exception:
            flash("Unexpected error updating field.", "danger")
        else:
            flash(f"Renamed field “{field_name}” → “{new_name}” in project “{project}”.", "success")
            return redirect(url_for("fields", project=project))

    # GET
    return render_template("fields_edit.html", project=project, field=field)


# ——— Delete Field ———
@app.route("/fields/delete/<project>/<field_name>", methods=["POST"])
def fields_delete(project, field_name):
    try:
        delete_field(project, field_name)
    except IntegrityError as e:
        # e.g. if some analysis rows depend on it
        flash(f"Cannot delete field “{field_name}”: related records exist.", "warning")
    except Exception:
        flash("Unexpected error deleting field.", "danger")
    else:
        flash(f"Deleted field “{field_name}” from project “{project}”.", "success")
    return redirect(url_for("fields", project=project))

@app.route("/project-posts", methods=["GET", "POST"])
def project_posts():
    # 1) Load dropdown data
    all_projects = [p["ProjectName"] for p in get_projects()]
    all_medias   = [m["MediaName"]   for m in get_media()]

    # 2) Read current filters from the URL
    project_filter = request.args.get("project_filter", "").strip()
    media_filter   = request.args.get("media_filter",   "").strip()

    if request.method == "POST":
        # 3) Pull & strip your form inputs
        proj      = request.form["project"].strip()
        media     = request.form["media"].strip()
        username  = request.form["username"].strip()
        time_post = request.form["time_posted"].strip()

        # 4) (Your existing validation goes here...)
        #    e.g. check required fields, timestamp format, catch IntegrityError, flash, etc.

        # 5) Insert link
        try:
            add_project_post(proj, media, username, time_post)
        except IntegrityError as e:
            # handle FK / dup / other errors...
            flash("Error linking post to project.", "danger")
        else:
            flash(f"Linked {media}/{username}@{time_post} → {proj}", "success")

        # 6) Redirect back *with* the current filters preserved
        return redirect(url_for(
            "project_posts",
            project_filter=project_filter,
            media_filter=media_filter
        ))

    # ——— GET ———
    # 7) Fetch *all* links, then apply filters
    links = get_project_posts()  # returns list of dicts
    if project_filter:
        links = [l for l in links if l["ProjectName"] == project_filter]
    if media_filter:
        links = [l for l in links if l["MediaName"]   == media_filter]

    # 8) Render template
    return render_template(
        "project_posts.html",
        all_projects=all_projects,
        all_medias=all_medias,
        project_filter=project_filter,
        media_filter=media_filter,
        links=links
    )

# ——— Edit Project-Post Link ———
@app.route(
  "/project-posts/edit/"
  "<project>/<media>/<username>/<path:time_posted>",
  methods=["GET", "POST"]
)
def project_posts_edit(project, media, username, time_posted):
    # 1) Normalize the URL time so it matches DB format
    try:
        norm_time = _normalize_timestamp(time_posted, "TimePosted")
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("project_posts"))

    # 2) Fetch all links for this project, then find the exact one
    rows = get_project_posts(project)
    link = next((
        r for r in rows
        if (r["ProjectName"] == project
            and r["MediaName"]   == media
            and r["Username"]    == username
            and _normalize_timestamp(str(r["TimePosted"]), "DB Time") == norm_time)
    ), None)

    if not link:
        flash(f"Link not found: {project}/{media}/{username}@{time_posted}", "warning")
        return redirect(url_for("project_posts"))

    if request.method == "POST":
        # Pull & normalize form inputs
        new_proj = request.form.get("project", "").strip()
        new_med  = request.form.get("media",   "").strip()
        new_usr  = request.form.get("username","").strip()
        new_time = request.form.get("time_posted","").strip()

        # Required?
        if not all([new_proj, new_med, new_usr, new_time]):
            flash("All fields are required.", "danger")
            return redirect(request.url)

        # Validate timestamp
        try:
            new_norm_time = _normalize_timestamp(new_time, "TimePosted")
        except ValueError as e:
            flash(str(e), "warning")
            return redirect(request.url)

        # Attempt update
        try:
            update_project_post(
                project, media, username, norm_time,
                ProjectName=new_proj,
                MediaName=new_med,
                Username=new_usr,
                TimePosted=new_norm_time
            )
        except IntegrityError as e:
            if e.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                flash("Project, media, user or post does not exist.", "warning")
            elif e.errno == errorcode.ER_DUP_ENTRY:
                flash("That link already exists.", "warning")
            else:
                flash("Database error updating link.", "danger")
        except Exception:
            flash("Unexpected error updating link.", "danger")
        else:
            flash("Link updated successfully!", "success")
            return redirect(url_for("project_posts"))

    # GET → render edit form
    return render_template("project_posts_edit.html", link=link)

# ——— Delete Project-Post Link ———
@app.route(
  "/project-posts/delete/<project>/<media>/<username>/<path:time_posted>",
  methods=["POST"]
)
def project_posts_delete(project, media, username, time_posted):
    try:
        delete_project_post(project, media, username, time_posted)
    except IntegrityError:
        flash("Cannot delete link: related records exist.", "warning")
    except Exception:
        flash("Unexpected error deleting link.", "danger")
    else:
        flash("Link deleted.", "success")
    return redirect(url_for("project_posts", project=project))

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

# ——— Edit Analysis ———
@app.route(
  "/analyses/edit/"
  "<project>/<field_name>/<media>/<username>/<path:time_posted>",
  methods=["GET", "POST"]
)
def analyses_edit(project, field_name, media, username, time_posted):
    # 1) Find the existing record
    rows = get_post_analyses(project)
    analysis = next((
      a for a in rows
      if (a["ProjectName"] == project
          and a["FieldName"]  == field_name
          and a["MediaName"]  == media
          and a["Username"]   == username
          and str(a["TimePosted"]) == time_posted)
    ), None)

    if not analysis:
        flash(f"Analysis not found: {project}/{field_name}/{media}/{username}@{time_posted}", "warning")
        return redirect(url_for("analyses", project=project))

    if request.method == "POST":
        # 2) Pull new value
        new_value = request.form.get("value", "").strip()
        if not new_value:
            flash("Value cannot be blank.", "danger")
            return redirect(request.url)

        # 3) Attempt update
        try:
            update_post_analysis(
                project, field_name,
                media, username, time_posted,
                new_value
            )
        except IntegrityError as e:
            flash("Database integrity error updating analysis.", "danger")
        except Exception as e:
            flash(f"Unexpected error: {e}", "danger")
        else:
            flash("Analysis updated successfully!", "success")
            return redirect(url_for("analyses", project=project))

    # GET → render edit form
    return render_template("analyses_edit.html", analysis=analysis)


# ——— Delete Analysis ———
@app.route(
  "/analyses/delete/"
  "<project>/<field_name>/<media>/<username>/<path:time_posted>",
  methods=["POST"]
)
def analyses_delete(project, field_name, media, username, time_posted):
    try:
        delete_post_analysis(project, field_name, media, username, time_posted)
    except IntegrityError:
        flash("Cannot delete analysis: related records exist.", "warning")
    except Exception as e:
        flash(f"Unexpected error: {e}", "danger")
    else:
        flash("Analysis deleted.", "success")
    return redirect(url_for("analyses", project=project))

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