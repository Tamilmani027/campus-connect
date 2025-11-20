# Placement Preparation Portal (FastAPI + Flask + MySQL)

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

## Notes
- Flask frontend calls FastAPI at `http://localhost:8000/`. Change `frontend_flask/utils/api_client.py` API_BASE if deploying separately.
- For production, use HTTPS, proper SECRET_KEY, and a reverse proxy (nginx). Use Alembic for DB migrations.
- This repo is a starter template — add search, pagination, file uploads, user accounts, and tests later.
