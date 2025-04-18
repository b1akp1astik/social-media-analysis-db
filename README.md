# Social Media Analysis DB Project

**Spring 2025, CS 5330/7330 Group Project**

## Project Goal

Build a general-purpose database system to store social media text posts and the results of multiple analysis projects. The application will allow:
- Entry of users, posts, reposts, projects, and analysis results
- Querying posts by media, time range, user, and poster name
- Querying projects to list associated posts and their analysis completion rates


## Repo Structure

```
├─ db/
│  ├─ schema/
│  │  └─ create_tables.sql        # DDL for all tables, FKs, and constraints
│  └─ dumps/
│     └─ social_media_dump.sql    # mysqldump export of schema + seed data
├─ app/
│  ├─ db_config.py.template      # Copy to db_config.py with your credentials
│  ├─ db.py                      # MySQL connection helper
│  ├─ crud.py                    # Basic CRUD functions (SocialMedia so far)
│  ├─ models.py                  # (Future) data models
│  └─ templates/
│     └─ index.html              # Sample Flask UI for SocialMedia list and add
├─ app.py                        # Flask web server entry point
├─ requirements.txt              # Python dependencies (Flask, mysql-connector)
└─ README.md                     # This file
```


## Prerequisites

- **Python 3.x**
- **MySQL** (or MariaDB) server
- **DBeaver** (or another MySQL client)
- **Git**


## Database Setup

Clone the repo and import the provided dump so you’re all working off the same `social_media` database.

### Method 1: Command‑Line Import
```bash
git clone <repo-url>
cd social-media-db/db/dumps
mysql -u <your_mysql_user> -p < social_media_dump.sql
```

### Method 2: DBeaver Backup/Restore
1. In DBeaver, right‑click your MySQL connection → **Tools → Restore**
2. Select `social_media_dump.sql` and run

### Method 3: Docker Compose (optional)
If you have Docker Desktop installed, from the repo root:
```bash
docker-compose up -d
```
This will start a MySQL container with `social_media` already initialized.


## Running the Application

1. Copy `app/db_config.py.template` → `app/db_config.py` and fill in your DB credentials.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Flask server:
   ```bash
   python app.py
   ```
4. Navigate to <http://127.0.0.1:5000> to view and add SocialMedia entries.


## What We Have So Far

- **Database schema** defined in `db/schema/create_tables.sql`
- **Database dump** (`social_media_dump.sql`) with sample data for SocialMedia
- **Python helpers** (`app/db.py`) and **CRUD** for the SocialMedia entity
- **Basic Flask UI** (`app.py` + `templates/index.html`) to list/add SocialMedia platforms


## Our Plan of Action

We’ve organized the work into four sprints, with clear deliverables and task ownership:

### Sprint 0: Kickoff & Environment Setup
- **Tasks:**
  - Create GitHub repo and branches (`main`, `develop`, `feature/*`).
  - Install and configure MySQL, Python, Flask, DBeaver, and Git.
  - Finalize ER‑model and relational schema in `db/schema/create_tables.sql`.
  - Verify local creation of the `social_media` database and tables.
  - Agree on coding standards and CI basics.

### Sprint 1: Core Database & CRUD Backend
- **Person A (DB Lead):**
  - Finalize DDL and seed scripts under `db/schema`.
  - Document SQL operations (`INSERT`, `SELECT`) in `db/sql/`.
- **Person B (Backend Lead):**
  - Implement Python DB connector and `run_query()` helper in `app/db.py`.
  - Build CRUD functions (`add_user()`, `add_post()`, etc.) in `app/crud.py`.
  - Write unit tests (pytest) against sample data.
- **Person C (UI Lead):**
  - Draft wireframes for data‑entry and query forms.
  - Scaffold static Flask templates for SocialMedia, User, Post, etc.

### Sprint 2: Web Interface & Query Features
- **Person A:**
  - Develop complex SQL queries for post/project searches and analysis summaries.
- **Person B:**
  - Expose queries as Python functions and Flask endpoints (`/search_posts`, `/search_experiments`).
- **Person C:**
  - Connect forms to real API endpoints, render results in HTML tables, and polish navigation.

### Sprint 3: Integration, Testing & Documentation
- **All Team Members:**
  - Conduct end‑to‑end testing of key workflows, report bugs, and fix.
  - Validate constraints (unique posts, date checks, partial analysis entry).
  - Prepare final report sections:
    - A: Database schema annotations (CREATE TABLE statements).
    - B: Installation & usage guide.
    - C: User manual with screenshots and sample flows.
  - Dry‑run demo and ensure each feature works seamlessly.


## Next Steps & Division of Work

| Person | Focus                                   | Deliverables                            |
|--------|-----------------------------------------|-----------------------------------------|
| A      | CRUD functions for User, Post, etc.     | `crud.py` functions and unit tests      |
| B      | Data‑entry UI forms for all entities    | Flask routes + templates (add/edit)     |
| C      | Query pages (posts & experiments)       | Flask routes + templates (search pages) |


## Contributing Guidelines

- **Branch naming**: `feature/<area>` (e.g. `feature/crud-post`)
- **Commit messages**: concise, imperative (“Add create_post function”)
- Open a **Pull Request** for each feature and assign a reviewer.

---

Let’s keep this repo in sync and iterate on functionality. Happy coding!

