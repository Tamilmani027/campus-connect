from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 5


# Handle imports for both module and direct execution
try:
    from .utils.app_client import (
        get_companies,
        get_company,
        get_company_experiences,
        submit_experience,
        get_resources,
        get_resumes,
        get_announcements,
        get_student_profile,
        API_TIMEOUT,
    )
except ImportError:
    # If running directly, add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from frontend_flask.utils.app_client import (
        get_companies,
        get_company,
        get_company_experiences,
        submit_experience,
        get_resources,
        get_resumes,
        get_announcements,
        get_student_profile,
        get_admin_analytics,
        get_student_analytics,
        get_drives,
        create_drive,
        apply_for_drive,
        get_my_applications,
        API_TIMEOUT,
    )

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET_KEY")


@app.context_processor
def inject_globals():
    """Inject global template variables."""
    return {"current_year": datetime.now().year}


# ---------- Route Protection Decorators ----------

def student_required(f):
    """Decorator to require student authentication."""
    def decorated_function(*args, **kwargs):
        if not session.get('student_token'):
            flash("Please login as a student to access this page.", "warning")
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


def admin_required(f):
    """Decorator to require admin authentication."""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_token'):
            flash("Please login as an admin to access this page.", "warning")
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


# ---------- Public Pages ----------

@app.route("/")
def home():
    """Home page - accessible to everyone."""
    # If already logged in, redirect to appropriate dashboard
    if session.get('student_token'):
        return redirect(url_for('student_dashboard'))
    if session.get('admin_token'):
        return redirect(url_for('admin_dashboard'))
    return render_template("home.html")

@app.route("/companies")
@student_required
def companies():
    """Companies page - requires student authentication."""
    try:
        companies = get_companies()
    except Exception as e:
        companies = []
        flash("Could not fetch companies from backend.", "danger")
    return render_template("companies.html", companies=companies)

@app.route("/company/<int:company_id>")
@student_required
def company_detail(company_id):
    """Company detail page - requires student authentication."""
    try:
        company = get_company(company_id)
        experiences = get_company_experiences(company_id)
    except Exception as e:
        flash("Failed to load company details.", "danger")
        return redirect(url_for("companies"))
    return render_template("company_detail.html", company=company, experiences=experiences)


@app.route("/resources")
@student_required
def resources_page():
    """Resources page - requires student authentication."""
    category = request.args.get("category")
    try:
        resources = get_resources(category=category)
    except Exception as e:
        resources = []
        flash("Unable to load resources at this moment", "warning")
    return render_template("resources.html", resources=resources, current_category=category)


@app.route("/resumes")
@student_required
def resumes_page():
    """Resumes page - requires student authentication."""
    try:
        resumes = get_resumes()
    except Exception as e:
        resumes = []
        flash("Unable to load resume templates at this moment", "warning")
    return render_template("resumes.html", resumes=resumes)


@app.route("/companies")
@student_required
def companies_page():
    try:
        companies = get_companies()
    except Exception:
        companies = []
        flash("Unable to load companies", "warning")
    return render_template("companies.html", companies=companies)


@app.route("/announcements")
@student_required
def announcements_page():
    """Announcements page - requires student authentication."""
    try:
        announcements = get_announcements()
    except Exception as e:
        announcements = []
        flash("Announcements service not reachable", "warning")
    return render_template("announcements.html", announcements=announcements)


@app.route("/student/dashboard")
@student_required
def student_dashboard():
    token = session.get("student_token")
    try:
        profile = get_student_profile(token)
    except Exception:
        profile = None
        flash("Unable to load student profile", "warning")
    try:
        resources = get_resources(token)
    except Exception:
        resources = []
    try:
        resumes = get_resumes(token)
    except Exception:
        resumes = []
    try:
        announcements = get_announcements(token)
    except Exception:
        announcements = []
    try:
        company_list = get_companies()
        company_lookup = {company["id"]: company for company in company_list}
    except Exception:
        company_lookup = {}
    try:
        resp = requests.get("http://localhost:8000/experiences", timeout=API_TIMEOUT)
        experiences = resp.json() if resp.status_code == 200 else []
    except Exception:
        experiences = []
    
    # New Data for Dashboards
    try:
        analytics = get_student_analytics(token)
    except Exception:
        analytics = {}
        
    try:
        drives = get_drives()
    except Exception:
        drives = []
        
    try:
        my_apps = get_my_applications(token)
    except Exception:
        my_apps = []

    return render_template(
        "student_dashboard.html",
        profile=profile,
        resources=resources,
        resumes=resumes,
        announcements=announcements,
        experiences=experiences,
        company_lookup=company_lookup,
        analytics=analytics,
        drives=drives,
        my_apps=my_apps
    )


@app.route("/practice")
@student_required
def practice_page():
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Fetch all questions (with limit for now)
        r = requests.get(f"{API_BASE_URL}/questions?limit=100", headers=headers, timeout=API_TIMEOUT)
        questions = r.json() if r.status_code == 200 else []
    except Exception:
        questions = []
        flash("Could not load questions", "warning")
    return render_template("practice.html", questions=questions)

@app.route("/practice/question/<int:question_id>")
@student_required
def practice_question_detail(question_id):
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Get Question Details
        q_req = requests.get(f"{API_BASE_URL}/questions/{question_id}", headers=headers, timeout=API_TIMEOUT)
        if q_req.status_code != 200:
            flash("Question not found", "danger")
            return redirect(url_for("practice_page"))
        question = q_req.json()
        
        # Get User Progress
        p_req = requests.get(f"{API_BASE_URL}/questions/{question_id}/progress", headers=headers, timeout=API_TIMEOUT)
        progress = p_req.json() if p_req.status_code == 200 else {}
        
    except Exception:
        flash("Error loading question data", "danger")
        return redirect(url_for("practice_page"))
        
    return render_template("practice_question.html", question=question, progress=progress)

@app.route("/practice/api/progress", methods=["POST"])
@student_required
def update_progress_proxy():
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    data = request.json
    question_id = data.get("question_id")
    
    if not question_id:
        return {"status": "error", "message": "Missing question_id"}, 400
        
    payload = {
        "status": data.get("status"),
        "submission_code": data.get("submission_code"),
        "user_notes": data.get("user_notes"),
        "is_bookmarked": data.get("is_bookmarked")
    }
    
    try:
        r = requests.post(f"{API_BASE_URL}/questions/{question_id}/progress", json=payload, headers=headers, timeout=API_TIMEOUT)
        if r.status_code == 200:
            return {"status": "success"}
        else:
            return {"status": "error", "message": r.text}, 500
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


@app.route("/forum")
@student_required
def forum_page():
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    tag = request.args.get("tag")
    url = f"{API_BASE_URL}/discussion/"
    if tag:
        url += f"?tag={tag}"
        
    try:
        r = requests.get(url, headers=headers, timeout=API_TIMEOUT)
        threads = r.json() if r.status_code == 200 else []
    except Exception:
        threads = []
        flash("Could not load forum threads", "warning")
    return render_template("forum.html", threads=threads)

@app.route("/forum/create", methods=["POST"])
@student_required
def forum_create():
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "title": request.form.get("title"),
        "content": request.form.get("content"),
        "tags": request.form.get("tags")
    }
    try:
        r = requests.post(f"{API_BASE_URL}/discussion/", json=payload, headers=headers, timeout=API_TIMEOUT)
        if r.status_code == 200:
            flash("Discussion started!", "success")
        else:
            flash("Failed to post: " + r.text, "danger")
    except Exception:
        flash("Network error", "danger")
    return redirect(url_for("forum_page"))

@app.route("/forum/<int:thread_id>")
@student_required
def forum_thread_detail(thread_id):
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{API_BASE_URL}/discussion/{thread_id}", headers=headers, timeout=API_TIMEOUT)
        if r.status_code != 200:
            flash("Thread not found", "danger")
            return redirect(url_for("forum_page"))
        thread = r.json()
    except Exception:
        flash("Error loading thread", "danger")
        return redirect(url_for("forum_page"))
    return render_template("forum_thread.html", thread=thread)

@app.route("/forum/<int:thread_id>/reply", methods=["POST"])
@student_required
def forum_reply(thread_id):
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"content": request.form.get("content")}
    try:
        r = requests.post(f"{API_BASE_URL}/discussion/{thread_id}/reply", json=payload, headers=headers, timeout=API_TIMEOUT)
        if r.status_code == 200:
            flash("Reply posted", "success")
        else:
            flash("Failed to reply: " + r.text, "danger")
    except Exception:
        flash("Network error", "danger")
    return redirect(url_for("forum_thread_detail", thread_id=thread_id))


@app.route("/study-planner")
@student_required
def study_planner_page():
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    subscription = None
    plans = []
    
    try:
        # Check for active subscription
        sub_req = requests.get(f"{API_BASE_URL}/planner/my-subscription", headers=headers, timeout=API_TIMEOUT)
        
        if sub_req.status_code == 200:
            subscription = sub_req.json()
            if not subscription: # API might return null/None for no subscription
                 subscription = None
        
        # If no subscription, fetch available plans
        if not subscription:
            plans_req = requests.get(f"{API_BASE_URL}/planner/plans", headers=headers, timeout=API_TIMEOUT)
            plans = plans_req.json() if plans_req.status_code == 200 else []
            
    except Exception:
        flash("Error loading planner data", "warning")
        
    return render_template("study_planner.html", subscription=subscription, plans=plans)

@app.route("/study-planner/subscribe/<int:plan_id>", methods=["POST"])
@student_required
def planner_subscribe(plan_id):
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.post(f"{API_BASE_URL}/planner/plans/{plan_id}/subscribe", headers=headers, timeout=API_TIMEOUT)
        if r.status_code == 200:
            flash("Successfully subscribed to plan!", "success")
        else:
            flash("Subscription failed: " + r.text, "danger")
    except Exception:
        flash("Network error", "danger")
    return redirect(url_for("study_planner_page"))

@app.route("/study-planner/task/<int:task_id>/complete", methods=["POST"])
@student_required
def planner_complete_task(task_id):
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.post(f"{API_BASE_URL}/planner/tasks/{task_id}/complete", headers=headers, timeout=API_TIMEOUT)
        if r.status_code == 200:
            return {"status": "success"}
        else:
            return {"status": "error", "message": r.text}, 500
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500







# ---------- Bookmarks ----------

@app.route("/bookmarks")
@student_required
def bookmarks():
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{API_BASE_URL}/bookmarks", headers=headers, timeout=API_TIMEOUT)
        bookmarks = r.json() if r.status_code == 200 else []
    except Exception:
        bookmarks = []
        flash("Could not load bookmarks", "warning")
    return render_template("bookmarks.html", bookmarks=bookmarks)

@app.route("/bookmarks/add", methods=["POST"])
@student_required
def add_bookmark():
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Expects JSON from AJAX or Form data
    if request.is_json:
        data = request.json
    else:
        data = request.form
        
    payload = {
        "entity_type": data.get("entity_type"),
        "entity_id": int(data.get("entity_id")),
        "note": data.get("note")
    }
    
    try:
        r = requests.post(f"{API_BASE_URL}/bookmarks", json=payload, headers=headers, timeout=API_TIMEOUT)
        if request.is_json:
            if r.status_code == 200:
                return {"status": "success", "message": "Bookmark added"}
            else:
                return {"status": "error", "message": r.text}, 400
        else:
            if r.status_code == 200:
                flash("Added to bookmarks", "success")
            else:
                flash("Failed to bookmark", "danger")
            return redirect(request.referrer or url_for('student_dashboard'))
    except Exception as e:
        if request.is_json:
            return {"status": "error", "message": str(e)}, 500
        flash("Network error", "danger")
        return redirect(request.referrer or url_for('student_dashboard'))

@app.route("/bookmarks/delete/<int:bookmark_id>", methods=["POST"])
@student_required
def delete_bookmark(bookmark_id):
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.delete(f"{API_BASE_URL}/bookmarks/{bookmark_id}", headers=headers, timeout=API_TIMEOUT)
        if r.status_code == 200:
            flash("Bookmark removed", "success")
        else:
            flash("Failed to remove bookmark", "danger")
    except Exception:
        flash("Network error", "danger")
    return redirect(url_for('bookmarks'))



@app.route("/bookmarks/api/check")
@student_required
def check_bookmark_status():
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    entity_type = request.args.get("type")
    entity_id = int(request.args.get("id"))
    
    try:
        r = requests.get(f"{API_BASE_URL}/bookmarks", headers=headers, timeout=API_TIMEOUT)
        if r.status_code == 200:
            bookmarks = r.json()
            for b in bookmarks:
                if b["entity_type"] == entity_type and b["entity_id"] == entity_id:
                    return {"is_bookmarked": True, "bookmark_id": b["id"]}
        return {"is_bookmarked": False}
    except Exception:
        return {"is_bookmarked": False}

@app.route("/bookmarks/api/toggle", methods=["POST"])
@student_required
def toggle_bookmark_status():
    token = session.get("student_token")
    headers = {"Authorization": f"Bearer {token}"}
    data = request.json
    entity_type = data.get("type")
    entity_id = int(data.get("id"))
    
    # First check if exists
    try:
        r = requests.get(f"{API_BASE_URL}/bookmarks", headers=headers, timeout=API_TIMEOUT)
        bookmark_id = None
        if r.status_code == 200:
            bookmarks = r.json()
            for b in bookmarks:
                if b["entity_type"] == entity_type and b["entity_id"] == entity_id:
                    bookmark_id = b["id"]
                    break
        
        if bookmark_id:
            # Delete
            requests.delete(f"{API_BASE_URL}/bookmarks/{bookmark_id}", headers=headers, timeout=API_TIMEOUT)
            return {"status": "removed"}
        else:
            # Create
            payload = {"entity_type": entity_type, "entity_id": entity_id, "note": "Saved from " + entity_type}
            requests.post(f"{API_BASE_URL}/bookmarks", json=payload, headers=headers, timeout=API_TIMEOUT)
            return {"status": "added"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


# ---------- Student Routes ----------

@app.route("/add-experience")
@student_required
def add_experience():
    token = session.get("student_token")
    try:
        profile = get_student_profile(token)
    except Exception:
        profile = None
        flash("Could not load student profile", "warning")
    try:
        companies = get_companies()
    except Exception:
        companies = []
        flash("Unable to load companies list", "warning")
    return render_template("add_experience.html", profile=profile, companies=companies)

@app.route("/submit-experience", methods=["POST"])
@student_required
def submit_exp():
    token = session.get("student_token")
    payload = {
        "student_name": request.form.get("student_name"),
        "department": request.form.get("department"),
        "batch": int(request.form.get("batch")) if request.form.get("batch") else None,
        "company_id": int(request.form.get("company_id")),
        "role": request.form.get("role"),
        "experience_text": request.form.get("experience_text"),
        "questions_faced": request.form.get("questions_faced"),
        "tips": request.form.get("tips"),
    }
    r = submit_experience(payload, token)
    if r.status_code == 200 or r.status_code == 201:
        flash("Experience submitted for review. Thank you!", "success")
    elif r.status_code == 401:
        flash("Authentication failed. Please login again.", "danger")
        session.pop("student_token", None)
        return redirect(url_for("student_login"))
    else:
        flash(f"Submission failed: {r.text}", "danger")
    return redirect(url_for("add_experience"))

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/admin-login", methods=["POST"])
def admin_login():
    username = request.form.get("username")
    password = request.form.get("password")
    try:
        r = requests.post(
            "http://localhost:8000/auth/login",
            json={"username": username, "password": password},
            timeout=API_TIMEOUT,
        )
        if r.status_code == 200:
            token = r.json().get("access_token")
            session["admin_token"] = token
            flash("Logged in as admin", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Login failed: " + r.text, "danger")
            return redirect(url_for("login_page"))
    except Exception as e:
        flash("Auth server not reachable.", "danger")
        return redirect(url_for("login_page"))

# Student auth (UI only placeholders)
@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            r = requests.post(
                "http://localhost:8000/students/login",
                json={"email": email, "password": password},
                timeout=API_TIMEOUT,
            )
            if r.status_code == 200:
                token = r.json().get("access_token")
                session["student_token"] = token
                flash("Logged in as student", "success")
                return redirect(url_for("student_dashboard"))
            else:
                flash("Login failed: " + r.text, "danger")
        except Exception:
            flash("Student auth server not reachable.", "danger")
    return render_template("auth_student_login.html")

@app.route("/student/register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        payload = {
            "name": request.form.get("name"),
            "department": request.form.get("department"),
            "batch": int(request.form.get("batch")) if request.form.get("batch") else None,
            "email": request.form.get("email"),
            "password": request.form.get("password"),
        }
        try:
            r = requests.post("http://localhost:8000/students/register", json=payload, timeout=API_TIMEOUT)
            if r.status_code == 200:
                flash("Registration successful. Please login.", "success")
                return redirect(url_for("student_login"))
            else:
                flash("Registration failed: " + r.text, "danger")
        except Exception:
            flash("Student API not reachable", "danger")
    return render_template("auth_student_register.html")


@app.route("/student/logout")
def student_logout():
    session.pop("student_token", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

# Admin registration (posts to FastAPI /auth/create-admin)
@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            r = requests.post(
                "http://localhost:8000/auth/create-admin",
                json={"username": username, "password": password},
                timeout=API_TIMEOUT,
            )
            if r.status_code == 200:
                flash("Admin created successfully. Please login.", "success")
                return redirect(url_for("login_page"))
            else:
                flash(f"Failed to create admin: {r.text}", "danger")
        except Exception:
            flash("Admin API not reachable", "danger")
    return render_template("auth_admin_register.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_token", None)
    flash("Admin session closed.", "info")
    return redirect(url_for("home"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get("http://localhost:8000/admin/pending-experiences", headers=headers, timeout=API_TIMEOUT)
        if r.status_code == 200:
            pending = r.json()
        else:
            pending = []
            flash("Failed to fetch pending experiences", "danger")
    except Exception:
        pending = []
        flash("Admin API not reachable", "danger")
    try:
        companies = get_companies()
    except Exception:
        companies = []
        flash("Failed to load companies list", "warning")
    # Use public endpoints for resources, resumes, and announcements
    try:
        resources = get_resources()  # Public endpoint, no token needed
    except Exception:
        resources = []
    try:
        resumes = get_resumes()  # Public endpoint, no token needed
    except Exception:
        resumes = []
    try:
        announcements = get_announcements()  # Public endpoint, no token needed
    except Exception:
        announcements = []
    
    # New Analytics Data
    try:
        analytics = get_admin_analytics(token)
    except Exception:
        analytics = {}
        
    return render_template(
        "admin_dashboard.html",
        pending=pending,
        companies=companies,
        resources=resources,
        resumes=resumes,
        announcements=announcements,
        analytics=analytics
    )

@app.route("/admin/questions/add", methods=["GET"])
@admin_required
def admin_add_question_page():
    return render_template("admin_add_question.html")

@app.route("/admin/questions/add", methods=["POST"])
@admin_required
def admin_add_question_submit():
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    q_type = request.form.get("type")
    
    payload = {
        "title": request.form.get("title"),
        "description": request.form.get("description"),
        "type": q_type,
        "difficulty": request.form.get("difficulty"),
        "topic": request.form.get("topic"),
        "company_tags": request.form.get("company_tags"),
        "solution": request.form.get("solution")
    }
    
    if q_type == "APTITUDE":
        payload["options"] = {
            "A": request.form.get("opt_a"),
            "B": request.form.get("opt_b"),
            "C": request.form.get("opt_c"),
            "D": request.form.get("opt_d")
        }
        payload["correct_option"] = request.form.get("correct_option")
        
    try:
        r = requests.post(f"{API_BASE_URL}/questions/", json=payload, headers=headers, timeout=API_TIMEOUT)
        if r.status_code == 200:
            flash("Question added successfully", "success")
        else:
            flash(f"Failed to add question: {r.text}", "danger")
    except Exception as e:
        flash(f"Error connecting to backend: {str(e)}", "danger")
        
    return redirect(url_for("admin_add_question_page"))

@app.route("/admin/resources", methods=["GET"])
@admin_required
def admin_resources_page():
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{API_BASE_URL}/content/resources", timeout=API_TIMEOUT)
        resources = r.json() if r.status_code == 200 else []
    except Exception:
        resources = []
    return render_template("admin_resources.html", resources=resources)

@app.route("/admin/resources/add", methods=["POST"])
@admin_required
def admin_add_resource():
    token = session.get("admin_token")
    # Note: requests handles multipart headers automatically when 'files' arg is used
    # But we need authentication.
    
    # Correct way to send Auth header + Multipart
    # We cannot construct headers manually with Content-Type for multipart, requests does it.
    # Just passing Authorization is enough.
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "title": request.form.get("title", ""),
        "description": request.form.get("description", ""),
        "category": request.form.get("category", "GENERAL"),
        "url": request.form.get("url", "")
    }
    
    files = {}
    if 'file' in request.files:
        f = request.files['file']
        if f.filename:
            # files = {'file': (filename, file_object, content_type)}
            files = {'file': (f.filename, f.stream, f.content_type)}
            
    # Force multipart/form-data even if no file is selected, because FastAPI expects it due to UploadFile
    if not files:
        files = {'_dummy': (None, '')}

    try:
        r = requests.post(
            f"{API_BASE_URL}/content/resources", 
            data=data, 
            files=files, 
            headers=headers, 
            timeout=30 # Larger timeout for uploads
        )
        if r.status_code == 200:
            flash("Resource uploaded successfully", "success")
        else:
            flash(f"Failed to upload: {r.text}", "danger")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        
    return redirect(url_for("admin_resources_page"))

@app.route("/admin/approve/<int:exp_id>")
@admin_required
def admin_approve(exp_id):
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(
        f"http://localhost:8000/admin/approve-experience/{exp_id}", headers=headers, timeout=API_TIMEOUT
    )
    if r.status_code == 200:
        flash("Approved", "success")
    else:
        flash("Action failed", "danger")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/reject/<int:exp_id>")
@admin_required
def admin_reject(exp_id):
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(
        f"http://localhost:8000/admin/reject-experience/{exp_id}", headers=headers, timeout=API_TIMEOUT
    )
    if r.status_code == 200:
        flash("Rejected", "success")
    else:
        flash("Action failed", "danger")
    return redirect(url_for("admin_dashboard"))

# Admin management actions (proxy to FastAPI)
@app.post("/admin/company/create")
@admin_required
def admin_company_create():
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": request.form.get("name"),
        "description": request.form.get("description"),
        "website": request.form.get("website"),
        "sector": request.form.get("sector"),
    }
    r = requests.post(
        "http://localhost:8000/admin/companies", json=payload, headers=headers, timeout=API_TIMEOUT
    )
    flash("Company created" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/company/update/<int:company_id>")
@admin_required
def admin_company_update(company_id: int):
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": request.form.get("name"),
        "description": request.form.get("description"),
        "website": request.form.get("website"),
        "sector": request.form.get("sector"),
    }
    r = requests.put(
        f"http://localhost:8000/admin/companies/{company_id}", json=payload, headers=headers, timeout=API_TIMEOUT
    )
    flash("Company updated" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/company/delete/<int:company_id>")
@admin_required
def admin_company_delete(company_id: int):
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.delete(
        f"http://localhost:8000/admin/companies/{company_id}", headers=headers, timeout=API_TIMEOUT
    )
    flash("Company removed" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/resource/create")
@admin_required
def admin_resource_create():
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": request.form.get("title"), "url": request.form.get("url"), "description": request.form.get("description")}
    r = requests.post(
        "http://localhost:8000/admin/resources", json=payload, headers=headers, timeout=API_TIMEOUT
    )
    flash("Resource added" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/resource/update/<int:rid>")
@admin_required
def admin_resource_update(rid: int):
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": request.form.get("title"), "url": request.form.get("url"), "description": request.form.get("description")}
    r = requests.put(
        f"http://localhost:8000/admin/resources/{rid}", json=payload, headers=headers, timeout=API_TIMEOUT
    )
    flash("Resource updated" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/resource/delete/<int:rid>")
@admin_required
def admin_resource_delete(rid: int):
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.delete(
        f"http://localhost:8000/admin/resources/{rid}", headers=headers, timeout=API_TIMEOUT
    )
    flash("Resource removed" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/resume/create")
@admin_required
def admin_resume_create():
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": request.form.get("title"), "url": request.form.get("url")}
    r = requests.post(
        "http://localhost:8000/admin/resumes", json=payload, headers=headers, timeout=API_TIMEOUT
    )
    flash("Resume sample added" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/resume/update/<int:rid>")
@admin_required
def admin_resume_update(rid: int):
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": request.form.get("title"), "url": request.form.get("url")}
    r = requests.put(
        f"http://localhost:8000/admin/resumes/{rid}", json=payload, headers=headers, timeout=API_TIMEOUT
    )
    flash("Resume template updated" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/resume/delete/<int:rid>")
@admin_required
def admin_resume_delete(rid: int):
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.delete(
        f"http://localhost:8000/admin/resumes/{rid}", headers=headers, timeout=API_TIMEOUT
    )
    flash("Resume template removed" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/announcement/create")
@admin_required
def admin_announcement_create():
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": request.form.get("title"), "content": request.form.get("content")}
    r = requests.post(
        "http://localhost:8000/admin/announcements", json=payload, headers=headers, timeout=API_TIMEOUT
    )
    flash("Announcement sent" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/announcement/update/<int:aid>")
@admin_required
def admin_announcement_update(aid: int):
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": request.form.get("title"), "content": request.form.get("content")}
    r = requests.put(
        f"http://localhost:8000/admin/announcements/{aid}", json=payload, headers=headers, timeout=API_TIMEOUT
    )
    flash("Announcement updated" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/announcement/delete/<int:aid>")
@admin_required
def admin_announcement_delete(aid: int):
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.delete(
        f"http://localhost:8000/admin/announcements/{aid}", headers=headers, timeout=API_TIMEOUT
    )
    flash("Announcement removed" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))


# --- Drives Management ---

@app.post("/admin/drive/create")
@admin_required
def admin_drive_create():
    token = session.get("admin_token")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "company_id": int(request.form.get("company_id")),
        "batch": int(request.form.get("batch")),
        "role": request.form.get("role"),
        "date": request.form.get("date"),
        "deadline": request.form.get("deadline"),
        "description": request.form.get("description"),
        "eligibility_criteria": request.form.get("eligibility_criteria")
    }
    r = create_drive(token, payload)
    flash("Drive created" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.route("/student/drive/apply/<int:drive_id>")
@student_required
def student_drive_apply(drive_id):
    token = session.get("student_token")
    r = apply_for_drive(token, drive_id)
    flash("Applied successfully" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("student_dashboard"))

import os

if __name__ == "__main__":
    # Ensure we can find templates and static files when running directly
    if not os.path.exists("templates"):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Use Render's dynamic PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
