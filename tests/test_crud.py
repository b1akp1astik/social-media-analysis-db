# tests/test_crud.py

import pytest
from datetime import datetime
from app.db import run_query
from app.crud import (
    add_media, add_user, add_post, add_repost,
    add_institute, add_project, add_field,
    add_project_post, add_post_analysis
)

@pytest.fixture(autouse=True)
def cleanup_db():
    # Runs before each test: delete all rows so tests stay independent.
    tables = [
        "PostAnalysis", "ProjectPost", "Field", "Project",
        "Repost", "Post", "User", "Institute", "SocialMedia"
    ]
    for t in tables:
        run_query(f"DELETE FROM {t}")
    yield
    # (optional) cleanup again after test
    for t in tables:
        run_query(f"DELETE FROM {t}")

def test_add_media_and_user():
    add_media("TestM")
    add_user("TestM", "u1", "Alice", "A", None, None, 30, "Other", False)
    rows = run_query(
        "SELECT * FROM User WHERE MediaName=%s AND Username=%s",
        ("TestM","u1"), fetch=True
    )
    assert len(rows) == 1
    assert rows[0]["FirstName"] == "Alice"

def test_add_post_and_repost():
    # prepare user
    add_media("TestM"); add_user("TestM","u1","A","B")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    add_post("TestM","u1", now, "Hello")
    posts = run_query(
        "SELECT * FROM Post WHERE MediaName=%s AND Username=%s",
        ("TestM","u1"), fetch=True
    )
    assert len(posts) == 1

    # repost it
    add_repost("TestM","u1", now, "TestM","u1", now)
    reps = run_query(
        "SELECT * FROM Repost WHERE OrigMedia=%s", ("TestM",), fetch=True
    )
    assert len(reps) == 1

def test_project_and_field_and_analysis():
    # institute + project
    add_institute("InstX")
    add_project("Proj1","MgrF","MgrL","InstX","2025-01-01","2025-12-31")
    projs = run_query(
        "SELECT * FROM Project WHERE ProjectName=%s", ("Proj1",), fetch=True
    )
    assert projs[0]["ManagerFirstName"] == "MgrF"

    # field
    add_field("Proj1","Sentiment")
    fields = run_query(
        "SELECT * FROM Field WHERE ProjectName=%s", ("Proj1",), fetch=True
    )
    assert fields[0]["FieldName"] == "Sentiment"

    # projectpost + postanalysis
    add_media("TestM"); add_user("TestM","u1","A","B")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    add_post("TestM","u1", now, "Test")
    add_project_post("Proj1","TestM","u1", now)
    add_post_analysis("Proj1","Sentiment","TestM","u1", now, "Positive")

    results = run_query(
        "SELECT * FROM PostAnalysis WHERE ProjectName=%s",
        ("Proj1",), fetch=True
    )
    assert results[0]["Value"] == "Positive"
