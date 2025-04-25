# app/crud.py
from app.db import run_query

def add_media(media_name):
    return run_query("INSERT INTO SocialMedia (MediaName) VALUES (%s)",
                     (media_name,))

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

def add_institute(name):
    return run_query("INSERT INTO Institute (InstituteName) VALUES (%s)", (name,))

def add_project(name, mgr_first, mgr_last, institute, start_date, end_date):
    sql = """
      INSERT INTO Project
        (ProjectName, ManagerFirstName, ManagerLastName,
         InstituteName, StartDate, EndDate)
      VALUES (%s,%s,%s,%s,%s,%s)
    """
    return run_query(sql, (name, mgr_first, mgr_last, institute, start_date, end_date))

def add_field(project_name, field_name):
    return run_query("INSERT INTO Field (ProjectName, FieldName) VALUES (%s,%s)",
                     (project_name, field_name))

def add_project_post(project_name, media, username, time_posted):
    sql = """
      INSERT INTO ProjectPost
        (ProjectName, MediaName, Username, TimePosted)
      VALUES (%s,%s,%s,%s)
    """
    return run_query(sql, (project_name, media, username, time_posted))

def add_post_analysis(project_name, field_name,
                      media, username, time_posted, value):
    sql = """
      INSERT INTO PostAnalysis
        (ProjectName, FieldName, MediaName, Username, TimePosted, Value)
      VALUES (%s,%s,%s,%s,%s,%s)
    """
    return run_query(sql, (project_name, field_name,
        media, username, time_posted, value))
