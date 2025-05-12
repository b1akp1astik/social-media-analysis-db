# Social Media Analysis DB Project

**Spring 2025, CS 5330/7330 Group Project**

---

## Project Goal

Build a general-purpose database system to store:
- **Social media text posts** (and reposts)  
- **Users** (per-platform)  
- **Analysis “projects”**, each defining a set of **fields**  
- **Results** of those analyses for each post  

The web-app lets you:
1. **Create & List** every entity: Media, Users, Posts, Reposts, Institutes, Projects, Fields, Project-Post links, Analyses  
2. **Search Posts** by media, time range, username or poster name (and see which projects have analyzed them)  
3. **Search Experiments** by project name (and see per-field coverage %)  

---

## Repo Structure

```
social-media-analysis-db/
│
├── db/
│   ├── schema/
│   │   └── create_tables.sql       # DDL: all CREATE TABLE, FKs & CHECKs
│   └── dumps/
│       └── social_media_dump.sql   # mysqldump of schema + sample seed data
│
├── app/
│   ├── db_config.py.template       # copy → db_config.py with your credentials
│   ├── db.py                       # MySQL connection & run_query() helper
│   └── crud.py                     # all add_/get_/find_ functions
│
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                   # global nav + common layout
│   ├── media.html                  # Create/List SocialMedia
│   ├── user.html                   # Create/List Users
│   ├── posts.html                  # Create/List Posts
│   ├── reposts.html                # Create/List Reposts
│   ├── institutes.html             # Create/List Institutes
│   ├── projects.html               # Create/List Projects
│   ├── fields.html                 # Create/List Fields
│   ├── project_posts.html          # Create/List Project-Post links
│   ├── analyses.html               # Create/List PostAnalyses
│   ├── search_posts.html           # Search Posts form & results
│   └── search_experiments.html     # Search Experiments form & results
│
├── tests/
│   └── test_crud.py                # pytest unit tests for crud layer
│
├── app.py                          # Flask application entry point
├── requirements.txt                # Flask, mysql-connector-python, pytest
├── .gitignore                      # ignore venv, pycache, db_config.py, etc.
└── README.md                       # this file
```

---

## Prerequisites

- **Python 3.7+**  
- **MySQL** (or MariaDB) server  
- **Git**  

Optional but recommended:  
- **DBeaver** (or another MySQL GUI)  

---

## Database Setup

1. **Clone** the repo:
   ```bash
   git clone https://github.com/b1akp1astik/social-media-analysis-db.git
   cd social-media-analysis-db
   ```

2. **Create** the empty database & tables:
   ```bash
   mysql -u root -p
   ```
   Then inside the `mysql>` prompt:
   ```sql
   CREATE DATABASE IF NOT EXISTS social_media;
   USE social_media;
   SOURCE db/schema/create_tables.sql;
   EXIT;
   ```

3. **(Optional)** Load sample data:
   Open db/dumps/social_media_dump.sql in DBeaver → Execute.

4. **Grant** your app user privileges (if you’re not using `root` on `db_config.py`):
   ```sql
   CREATE USER 'cs5330'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON social_media.* TO 'cs5330'@'localhost';
   FLUSH PRIVILEGES;
   ```

---

## Configuration

1. Copy the template:
   ```bash
   cp app/db_config.py.template app/db_config.py
   ```
2. Edit `app/db_config.py` and fill in your:
   ```python
   # app/db_config.py
   DB_HOST     = "localhost"
   DB_USER     = "cs5330"
   DB_PASS     = "your_password"
   DB_NAME     = "social_media"
   DB_PORT     = 3306

   ```

---

## Install & Run

1. **Install** dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. **Launch** the Flask app:
   ```bash
   python app.py
   ```
3. **Open** your browser at <http://127.0.0.1:5000>  
   The home page will redirect to **/media**; use the nav bar to explore all screens.

---

## Running Tests

```bash
pytest -q
```

This runs unit tests against the CRUD functions to ensure your database operations work.

---

## Our Plan of Action

We’re working in four sprints, each with clear roles:

| Sprint | Focus                                   | Deliverables                                        |
|--------|-----------------------------------------|-----------------------------------------------------|
| 0      | Kickoff & Environment                   | ER model, schema SQL, repo setup, CI basics         |
| 1      | Core DB & CRUD                          | DDL scripts, `db.py`, CRUD functions, unit tests    |
| 2      | Web UI & Queries                        | Flask routes, Jinja templates, advanced search      |
| 3      | Integration, Testing & Documentation    | E2E QA, final report (ER diagram, schema, screenshots) |

### Team Roles

- **DB Lead**: finalize schema & seed data, write complex SQL  
- **Backend Lead**: build Python DB connector, CRUD & query functions  
- **UI Lead**: scaffold Flask views, Jinja templates & navigation  

