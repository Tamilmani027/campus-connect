from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Handle imports for both module and direct execution
try:
    from .utils.app_client import get_companies, get_company, get_company_experiences, submit_experience
except ImportError:
    # If running directly, add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from frontend_flask.utils.app_client import get_companies, get_company, get_company_experiences, submit_experience

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET_KEY")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/companies")
def companies():
    try:
        companies = get_companies()
    except Exception as e:
        companies = []
        flash("Could not fetch companies from backend.", "danger")
    return render_template("companies.html", companies=companies)

@app.route("/company/<int:company_id>")
def company_detail(company_id):
    try:
        company = get_company(company_id)
        experiences = get_company_experiences(company_id)
    except Exception as e:
        flash("Failed to load company details.", "danger")
        return redirect(url_for("companies"))
    return render_template("company_detail.html", company=company, experiences=experiences)

@app.route("/add-experience")
def add_experience():
    return render_template("add_experience.html")

@app.route("/submit-experience", methods=["POST"])
def submit_exp():
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
    token = session.get("student_token")
    r = submit_experience(payload, token)
    if r.status_code == 200 or r.status_code == 201:
        flash("Experience submitted for review. Thank you!", "success")
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
        r = requests.post("http://localhost:8000/auth/login", json={"username": username, "password": password})
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
            r = requests.post("http://localhost:8000/students/login", json={"email": email, "password": password})
            if r.status_code == 200:
                token = r.json().get("access_token")
                session["student_token"] = token
                flash("Logged in as student", "success")
                return redirect(url_for("home"))
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
            r = requests.post("http://localhost:8000/students/register", json=payload)
            if r.status_code == 200:
                flash("Registration successful. Please login.", "success")
                return redirect(url_for("student_login"))
            else:
                flash("Registration failed: " + r.text, "danger")
        except Exception:
            flash("Student API not reachable", "danger")
    return render_template("auth_student_register.html")

# Admin registration (posts to FastAPI /auth/create-admin)
@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            r = requests.post("http://localhost:8000/auth/create-admin", json={"username": username, "password": password})
            if r.status_code == 200:
                flash("Admin created successfully. Please login.", "success")
                return redirect(url_for("login_page"))
            else:
                flash(f"Failed to create admin: {r.text}", "danger")
        except Exception:
            flash("Admin API not reachable", "danger")
    return render_template("auth_admin_register.html")

@app.route("/admin")
def admin_dashboard():
    token = session.get("admin_token")
    if not token:
        flash("Login required", "warning")
        return redirect(url_for("login_page"))
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get("http://localhost:8000/admin/pending-experiences", headers=headers)
        if r.status_code == 200:
            pending = r.json()
        else:
            pending = []
            flash("Failed to fetch pending experiences", "danger")
    except Exception:
        pending = []
        flash("Admin API not reachable", "danger")
    return render_template("admin_dashboard.html", pending=pending)

@app.route("/admin/approve/<int:exp_id>")
def admin_approve(exp_id):
    token = session.get("admin_token")
    if not token:
        flash("Login required", "warning")
        return redirect(url_for("login_page"))
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(f"http://localhost:8000/admin/approve-experience/{exp_id}", headers=headers)
    if r.status_code == 200:
        flash("Approved", "success")
    else:
        flash("Action failed", "danger")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/reject/<int:exp_id>")
def admin_reject(exp_id):
    token = session.get("admin_token")
    if not token:
        flash("Login required", "warning")
        return redirect(url_for("login_page"))
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.put(f"http://localhost:8000/admin/reject-experience/{exp_id}", headers=headers)
    if r.status_code == 200:
        flash("Rejected", "success")
    else:
        flash("Action failed", "danger")
    return redirect(url_for("admin_dashboard"))

# Admin management actions (proxy to FastAPI)
@app.post("/admin/company/create")
def admin_company_create():
    token = session.get("admin_token")
    if not token:
        flash("Login required", "warning")
        return redirect(url_for("login_page"))
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": request.form.get("name"),
        "description": request.form.get("description"),
        "website": request.form.get("website"),
        "sector": request.form.get("sector"),
    }
    r = requests.post("http://localhost:8000/admin/companies", json=payload, headers=headers)
    flash("Company created" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/resource/create")
def admin_resource_create():
    token = session.get("admin_token")
    if not token:
        flash("Login required", "warning")
        return redirect(url_for("login_page"))
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": request.form.get("title"), "url": request.form.get("url"), "description": request.form.get("description")}
    r = requests.post("http://localhost:8000/admin/resources", json=payload, headers=headers)
    flash("Resource added" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/resume/create")
def admin_resume_create():
    token = session.get("admin_token")
    if not token:
        flash("Login required", "warning")
        return redirect(url_for("login_page"))
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": request.form.get("title"), "url": request.form.get("url")}
    r = requests.post("http://localhost:8000/admin/resumes", json=payload, headers=headers)
    flash("Resume sample added" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/announcement/create")
def admin_announcement_create():
    token = session.get("admin_token")
    if not token:
        flash("Login required", "warning")
        return redirect(url_for("login_page"))
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": request.form.get("title"), "content": request.form.get("content")}
    r = requests.post("http://localhost:8000/admin/announcements", json=payload, headers=headers)
    flash("Announcement sent" if r.status_code == 200 else f"Failed: {r.text}", "success" if r.status_code == 200 else "danger")
    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    # Ensure we can find templates and static files when running directly
    import os
    if not os.path.exists("templates"):
        # If running from project root, change to frontend_flask directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app.run(port=5000, debug=True)
