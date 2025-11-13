from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from datetime import datetime

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
    try:
        resources = get_resources()
    except Exception as e:
        resources = []
        flash("Unable to load resources at this moment", "warning")
    return render_template("resources.html", resources=resources)


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
    return render_template(
        "student_dashboard.html",
        profile=profile,
        resources=resources,
        resumes=resumes,
        announcements=announcements,
        experiences=experiences,
        company_lookup=company_lookup,
    )


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
    return render_template(
        "admin_dashboard.html",
        pending=pending,
        companies=companies,
        resources=resources,
        resumes=resumes,
        announcements=announcements,
    )

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

if __name__ == "__main__":
    # Ensure we can find templates and static files when running directly
    import os
    if not os.path.exists("templates"):
        # If running from project root, change to frontend_flask directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app.run(port=5000, debug=True)
