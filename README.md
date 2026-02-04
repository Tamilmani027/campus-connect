Here’s a polished, professional, and well-structured version of your README. I’ve refined the formatting, improved clarity, and made it presentation-ready for recruiters, collaborators, or open-source contributors:

---

# 📘 Campus-Connect

## Project Overview
**Campus-Connect** is a comprehensive, full-stack web application designed to streamline campus placement preparation.  
Built with a high-performance **FastAPI** backend and a dynamic **Flask** frontend, the platform bridges the gap between students and resources.  

It provides:
- A structured environment for students to master aptitude, coding, and soft skills.  
- Powerful administrative tools for managing content and tracking engagement.  

---

## Tech Stack
- **Backend:** FastAPI, SQLAlchemy, MySQL  
- **Frontend:** Flask, Jinja2  
- **Deployment:** Uvicorn / Gunicorn, Render.com  
- **Utilities:** Docker (optional), virtualenv  

---

## Key Features

### Student Role
- **Interactive Dashboard**
  - Centralized hub for aptitude, coding, interview prep, and HR resources.
  - Access company-specific preparation guides and skill roadmaps.
- **Coding & DSA Arena**
  - Repository of coding questions categorized by company.
  - Difficulty-tiered problems (Easy / Medium / Hard) with detailed solutions.
- **Communication & HR Prep**
  - Curated database of 50+ HR interview questions with model answers.
  - Guides on soft skills and body language for professional impact.
- **Collaborative Discussion Forum**
  - Peer-to-peer learning and doubt resolution.
  - Dedicated threads for company-specific discussions.
- **Smart Study Planner**
  - Customizable study roadmaps (30-day / 60-day / 90-day).
  - Daily progress tracking with interactive checklists.
- **Bookmarks & Saved Items**
  - Save interview experiences, DSA questions, and notes for quick revision.

---

### Admin Role
- **Analytics Dashboard**
  - Overview of student engagement metrics and content statistics.
- **Company Material Management**
  - Create and manage company profiles.
  - Upload Previous Year Questions (PYQs) and fresh coding/aptitude sets.
- **Content Management System (CMS)**
  - Aptitude: Manage quantitative, logical, and verbal ability questions.
  - Coding: Add DSA questions with test cases and curated practice sheets.
- **Resource Repository**
  - Upload and organize learning materials (PDF notes, cheat sheets, video links, PPTs).

---

## Prerequisites
- Python **3.9+**  
- MySQL server  
- (Optional) `virtualenv`  

---

## Setup Instructions

### 1. Database Setup
```bash
# Edit DB name if required
mysql -u root -p < mysql_schema/placement_portal.sql
```

---

### 2. Backend (FastAPI)
```bash
cd backend_fastapi
pip install -r requirements.txt
```

- Configure environment variables (`.env` or export):
  ```
  MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB, SECRET_KEY
  ```

- Run locally:
  ```bash
  python -m uvicorn backend_fastapi.main:app --reload --port 8000
  ```
  *(On Windows, use `python -m uvicorn` if `uvicorn` is not found)*

#### Deployment Notes (Render / Other Hosts)
- Use the provided `app.py` wrapper if `backend_fastapi` imports fail due to PYTHONPATH issues.  
- Example start commands:
  ```bash
  # Uvicorn
  python -m uvicorn app:app --host 0.0.0.0 --port $PORT

  # Gunicorn (recommended for production)
  gunicorn -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:$PORT
  ```

- (Optional) Create an admin:
  ```http
  POST /auth/create-admin
  {
    "username": "admin",
    "password": "password"
  }
  ```

---

### 3. Frontend (Flask)
```bash
# From project root
pip install -r frontend_flask/requirements.txt
```

Run the application:
- **Method 1 (Recommended):**
  ```bash
  python -m frontend_flask.app
  ```
- **Method 2:**
  ```bash
  cd frontend_flask && python app.py
  ```

Visit: [http://localhost:5000](http://localhost:5000)

---


## Next Steps
- Add CI/CD pipelines (GitHub Actions / Jenkins).  
- Integrate Docker for containerized deployment.  
- Expand analytics with Power BI dashboards.  

---
