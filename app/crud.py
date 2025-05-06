# app/crud.py
from app.db import run_query

def get_media():
    """Return all rows from SocialMedia."""
    return run_query("SELECT * FROM SocialMedia", fetch=True)


def add_media(media_name):
    return run_query("INSERT INTO SocialMedia (MediaName) VALUES (%s)",
                     (media_name,))

def get_media(media_name=None):
    if media_name:
        return run_query(
            "SELECT * FROM SocialMedia WHERE MediaName = %s", 
            (media_name,), 
            fetch=True
        )
    return run_query("SELECT * FROM SocialMedia", fetch=True)

def update_media(old_name, new_name):
    return run_query(
        "UPDATE SocialMedia SET MediaName = %s WHERE MediaName = %s", 
        (new_name, old_name)
    )

def delete_media(media_name):
    return run_query(
        "DELETE FROM SocialMedia WHERE MediaName = %s", 
        (media_name,)
    )

# ------------------ User ------------------

def add_user(media, username, first_name, last_name,
             country_birth=None, country_res=None,
             age=None, gender=None, is_verified=False):
    sql = """
      INSERT INTO User
        (MediaName, Username, FirstName, LastName,
         CountryOfBirth, CountryOfResidence, Age, Gender, IsVerified)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    return run_query(sql, (media, username, first_name, last_name,
        country_birth, country_res, age, gender, is_verified))

def get_user(media, username=None):
    if username:
        return run_query(
            "SELECT * FROM User WHERE MediaName = %s AND Username = %s",
            (media, username), fetch=True
        )
    return run_query(
        "SELECT * FROM User WHERE MediaName = %s", 
        (media,), fetch=True
    )

def update_user(media, username, **fields):
    cols = []
    vals = []
    for key, val in fields.items():
        cols.append(f"{key} = %s")
        vals.append(val)
    vals.extend([media, username])
    sql = f"UPDATE User SET {', '.join(cols)} WHERE MediaName = %s AND Username = %s"
    return run_query(sql, tuple(vals))

def delete_user(media, username):
    return run_query(
        "DELETE FROM User WHERE MediaName = %s AND Username = %s",
        (media, username)
    )

# ------------------ Post ------------------

def add_post(media, username, time_posted, text_content,
             city=None, state=None, country=None,
             likes=0, dislikes=0, has_multimedia=False):
    sql = """
      INSERT INTO Post
        (MediaName, Username, TimePosted, TextContent,
         City, State, Country, Likes, Dislikes, HasMultimedia)
      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    return run_query(sql, (media, username, time_posted, text_content,
        city, state, country, likes, dislikes, has_multimedia))

def get_post(media=None, username=None):
    base = "SELECT * FROM Post"
    params = []
    conds = []
    if media:
        conds.append("MediaName = %s"); params.append(media)
    if username:
        conds.append("Username = %s"); params.append(username)
    if conds:
        base += " WHERE " + " AND ".join(conds)
    return run_query(base, tuple(params), fetch=True)

def update_post(media, username, time_posted, **fields):
    cols = []
    vals = []
    for key, val in fields.items():
        cols.append(f"{key} = %s")
        vals.append(val)
    vals.extend([media, username, time_posted])
    sql = f"UPDATE Post SET {', '.join(cols)} WHERE MediaName = %s AND Username = %s AND TimePosted = %s"
    return run_query(sql, tuple(vals))

def delete_post(media, username, time_posted):
    return run_query(
        "DELETE FROM Post WHERE MediaName = %s AND Username = %s AND TimePosted = %s",
        (media, username, time_posted)
    )

# ------------------ Repost ------------------

def add_repost(orig_media, orig_user, orig_time,
               rep_media, rep_user, repost_time):
    sql = """
      INSERT INTO Repost
        (OrigMedia, OrigUser, OrigTime,
         ReposterMedia, ReposterUser, RepostTime)
      VALUES (%s,%s,%s,%s,%s,%s)
    """
    return run_query(sql, (orig_media, orig_user, orig_time,
        rep_media, rep_user, repost_time))

def get_repost(orig_media=None):
    if orig_media:
        return run_query(
            "SELECT * FROM Repost WHERE OrigMedia = %s", (orig_media,), fetch=True
        )
    return run_query("SELECT * FROM Repost", fetch=True)

# app/crud.py

def get_reposts(orig_media=None):
    """Return all reposts, optionally filtered by original media."""
    return get_repost(orig_media)


def update_repost(orig_media, orig_user, orig_time, repost_time, **fields):
    cols=[]; vals=[]
    for k,v in fields.items(): cols.append(f"{k} = %s"); vals.append(v)
    vals.extend([orig_media, orig_user, orig_time, repost_time])
    sql = f"UPDATE Repost SET {', '.join(cols)} WHERE OrigMedia=%s AND OrigUser=%s AND OrigTime=%s AND RepostTime=%s"
    return run_query(sql, tuple(vals))

def delete_repost(orig_media, orig_user, orig_time, repost_time):
    return run_query(
        "DELETE FROM Repost WHERE OrigMedia=%s AND OrigUser=%s AND OrigTime=%s AND RepostTime=%s",
        (orig_media, orig_user, orig_time, repost_time)
    )

# ------------------ Institute ------------------

def add_institute(name):
    return run_query("INSERT INTO Institute (InstituteName) VALUES (%s)", (name,))

def get_institute(name=None):
    if name:
        return run_query("SELECT * FROM Institute WHERE InstituteName=%s", (name,), fetch=True)
    return run_query("SELECT * FROM Institute", fetch=True)

def update_institute(old, new):
    return run_query(
        "UPDATE Institute SET InstituteName=%s WHERE InstituteName=%s", (new, old)
    )

def delete_institute(name):
    return run_query("DELETE FROM Institute WHERE InstituteName=%s", (name,))

# ------------------ Project ------------------

def add_project(name, mgr_first, mgr_last, institute, start_date, end_date):
    sql="""
      INSERT INTO Project
        (ProjectName, ManagerFirstName, ManagerLastName,
         InstituteName, StartDate, EndDate)
      VALUES (%s,%s,%s,%s,%s,%s)
    """
    return run_query(sql, (name, mgr_first, mgr_last, institute, start_date, end_date))

def get_project(name=None):
    if name:
        return run_query("SELECT * FROM Project WHERE ProjectName=%s", (name,), fetch=True)
    return run_query("SELECT * FROM Project", fetch=True)

def update_project(name, **fields):
    cols=[]; vals=[]
    for k,v in fields.items(): cols.append(f"{k}=%s"); vals.append(v)
    vals.append(name)
    sql = f"UPDATE Project SET {', '.join(cols)} WHERE ProjectName=%s"
    return run_query(sql, tuple(vals))

def delete_project(name):
    return run_query("DELETE FROM Project WHERE ProjectName=%s", (name,))

# ------------------ Field ------------------

def add_field(project_name, field_name):
    return run_query("INSERT INTO Field (ProjectName, FieldName) VALUES (%s,%s)", (project_name, field_name))

def get_field(project_name=None):
    if project_name:
        return run_query("SELECT * FROM Field WHERE ProjectName=%s", (project_name,), fetch=True)
    return run_query("SELECT * FROM Field", fetch=True)

def update_field(project_name, old_field, new_field):
    return run_query(
        "UPDATE Field SET FieldName=%s WHERE ProjectName=%s AND FieldName=%s",
        (new_field, project_name, old_field)
    )

def delete_field(project_name, field_name):
    return run_query(
        "DELETE FROM Field WHERE ProjectName=%s AND FieldName=%s",
        (project_name, field_name)
    )

# ------------------ ProjectPost ------------------

def add_project_post(project_name, media, username, time_posted):
    sql="""
      INSERT INTO ProjectPost
        (ProjectName, MediaName, Username, TimePosted)
      VALUES (%s,%s,%s,%s)
    """
    return run_query(sql, (project_name, media, username, time_posted))

def get_project_post(project_name=None):
    if project_name:
        return run_query("SELECT * FROM ProjectPost WHERE ProjectName=%s", (project_name,), fetch=True)
    return run_query("SELECT * FROM ProjectPost", fetch=True)

def update_project_post(project_name, media, username, time_posted, **fields):
    cols=[]; vals=[]
    for k,v in fields.items(): cols.append(f"{k}=%s"); vals.append(v)
    vals.extend([project_name, media, username, time_posted])
    sql = f"UPDATE ProjectPost SET {', '.join(cols)} WHERE ProjectName=%s AND MediaName=%s AND Username=%s AND TimePosted=%s"
    return run_query(sql, tuple(vals))

def delete_project_post(project_name, media, username, time_posted):
    return run_query(
        "DELETE FROM ProjectPost WHERE ProjectName=%s AND MediaName=%s AND Username=%s AND TimePosted=%s",
        (project_name, media, username, time_posted)
    )

# ------------------ PostAnalysis ------------------

def add_post_analysis(project_name, field_name,
                      media, username, time_posted, value):
    sql="""
      INSERT INTO PostAnalysis
        (ProjectName, FieldName, MediaName, Username, TimePosted, Value)
      VALUES (%s,%s,%s,%s,%s,%s)
    """
    return run_query(sql, (project_name, field_name,
        media, username, time_posted, value))

def get_post_analysis(project_name=None):
    if project_name:
        return run_query("SELECT * FROM PostAnalysis WHERE ProjectName=%s", (project_name,), fetch=True)
    return run_query("SELECT * FROM PostAnalysis", fetch=True)

def update_post_analysis(project_name, field_name, media, username, time_posted, value):
    sql = """
      UPDATE PostAnalysis
      SET Value=%s
      WHERE ProjectName=%s AND FieldName=%s AND MediaName=%s AND Username=%s AND TimePosted=%s
    """
    return run_query(sql, (value, project_name, field_name, media, username, time_posted))

def delete_post_analysis(project_name, field_name, media, username, time_posted):
    sql = """
      DELETE FROM PostAnalysis
      WHERE ProjectName=%s AND FieldName=%s AND MediaName=%s AND Username=%s AND TimePosted=%s
    """
    return run_query(sql, (project_name, field_name, media, username, time_posted))

def get_users(media=None):
    return get_user(media)   # returns all users for a media if given, or empty list otherwise

def get_posts(media=None, username=None):
    """
    Return all posts, optionally filtered by media name and/or username.
    """
    sql = "SELECT * FROM Post"
    params = []
    clauses = []
    if media:
        clauses.append("MediaName=%s")
        params.append(media)
    if username:
        clauses.append("Username=%s")
        params.append(username)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    return run_query(sql, params, fetch=True)

def get_institutes():
    """Return all rows from Institute."""
    return run_query("SELECT * FROM Institute", fetch=True)

def get_projects():
    """Return all rows from Project."""
    return run_query("SELECT * FROM Project", fetch=True)

def get_fields(project_name=""):
    """
    Return all fields; if project_name is given, only fields for that project.
    """
    sql = "SELECT * FROM Field"
    params = []
    if project_name:
        sql += " WHERE ProjectName=%s"
        params.append(project_name)
    return run_query(sql, params, fetch=True)

def get_project_posts(project_name=""):
    """
    Return all ProjectPost rows, optionally filtered by project_name.
    """
    return get_project_post(project_name)

def get_post_analyses(project_name=""):
    """
    Return all PostAnalysis rows, optionally filtered by project_name.
    """
    return get_post_analysis(project_name)

def find_posts(media=None, username=None, first=None, last=None, 
               start=None, end=None):
    """
    Return posts filtered by:
      - media (exact)
      - username (exact)
      - poster first name (exact)
      - poster last name (exact)
      - start/end timestamps (inclusive)
    """
    sql = """
      SELECT p.*, u.FirstName, u.LastName
      FROM Post p
      JOIN User u ON p.MediaName=u.MediaName AND p.Username=u.Username
    """
    clauses, params = [], []
    if media:
        clauses.append("p.MediaName=%s"); params.append(media)
    if username:
        clauses.append("p.Username=%s"); params.append(username)
    if first:
        clauses.append("u.FirstName=%s"); params.append(first)
    if last:
        clauses.append("u.LastName=%s"); params.append(last)
    if start:
        clauses.append("p.TimePosted >= %s"); params.append(start)
    if end:
        clauses.append("p.TimePosted <= %s"); params.append(end)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY p.TimePosted DESC"
    return run_query(sql, params, fetch=True)
