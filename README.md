# Campus-Connect (FastAPI + Flask + MySQL)

## Project Overview
The Campus-Connect is a comprehensive, full-stack web application designed to streamline campus placement preparation. Built with a high-performance **FastAPI** backend and a dynamic **Flask** frontend, the platform bridges the gap between students and resources. It offers a structured environment for students to master aptitude, coding, and soft skills, while providing administrators with powerful tools to manage content and track engagement.

## Key Features

### 🎓 Student Role
*   **Interactive Dashboard**
    *   Centralized hub for aptitude, coding, interview prep, and HR resources.
    *   Access company-specific preparation guides and skill roadmaps.
*   **Coding & DSA Arena**
    *   Extensive repository of coding questions categorized by company.
    *   Difficulty-tiered problems (Easy / Medium / Hard) with detailed solutions and explanations.
*   **Communication & HR Prep**
    *   Curated database of 50+ HR interview questions with model answers.
    *   Guides on soft skills and body language for professional impact.
*   **Collaborative Discussion Forum**
    *   Platform for peer-to-peer learning and doubt resolution.
    *   Dedicated threads for company-specific discussions.
*   **Smart Study Planner**
    *   Customizable study roadmaps (30-day / 60-day / 90-day).
    *   Daily progress tracking with interactive checklists.
*   **Bookmarks & Saved Items**
    *   Save feature for refined revision of interview experiences, DSA questions, and notes.

### 🛠️ Admin Role
*   **Analytics Dashboard**
    *   Overview of student engagement metrics and content statistics.
*   **Company Material Management**
    *   Create and manage company profiles.
    *   Upload Previous Year Questions (PYQs) and fresh coding/aptitude sets.
*   **Content Management System (CMS)**
    *   **Aptitude**: Manage quantitative, logical, and verbal ability questions.
    *   **Coding**: Add DSA questions with test cases and curated practice sheets.
*   **Resource Repository**
    *   Upload and organize learning materials including PDF notes, cheat sheets, video links, and PPTs.

## Prerequisites
- Python 3.9+

- MySQL server
- (Optional) virtualenv

## Steps

1. Create the MySQL DB:
   - Edit mysql_schema/placement_portal.sql if you need different DB name.
   - Run SQL: `mysql -u root -p < mysql_schema/placement_portal.sql`

2. Backend (FastAPI)
   - cd backend_fastapi
   - pip install -r requirements.txt
   - create a `.env` or export env vars:
     MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB, SECRET_KEY   
   - Run:
      `python -m uvicorn backend_fastapi.main:app --reload --port 8000`
      (On Windows, if `uvicorn` command is not found, use `python -m uvicorn` instead)

  Deployment note (Render.com / other hosts):

  - If your host cannot import the `backend_fastapi` package due to PYTHONPATH differences, use the provided top-level `app.py` as the entrypoint. Example start command for Render or a Procfile:

    - Uvicorn directly:
      `python -m uvicorn app:app --host 0.0.0.0 --port $PORT`

    - Or with Gunicorn + Uvicorn workers (recommended for production):
      `gunicorn -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:$PORT`

  This wrapper ensures the repository root is on `sys.path` so package imports like `backend_fastapi.*` resolve correctly.
   - (optional) Create an admin:
     POST `/auth/create-admin` with JSON `{"username":"admin","password":"password"}`

3. Frontend (Flask)
   - From project root, install dependencies:
     `pip install -r frontend_flask/requirements.txt`
   - Run (choose one method):
     - **Method 1 (Recommended)**: `python -m frontend_flask.app`
     - **Method 2**: `cd frontend_flask && python app.py`
   - Visit: http://localhost:5000


