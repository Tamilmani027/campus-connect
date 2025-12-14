import requests
from urllib.parse import urljoin
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE", "http://localhost:8000/")
API_TIMEOUT = float(os.getenv("API_TIMEOUT", 6))

def get_companies():
    r = requests.get(urljoin(API_BASE, "companies/"), timeout=API_TIMEOUT)
    r.raise_for_status()
    return r.json()

def get_company(company_id):
    r = requests.get(urljoin(API_BASE, f"companies/{company_id}"), timeout=API_TIMEOUT)
    r.raise_for_status()
    return r.json()

def get_company_experiences(company_id):
    r = requests.get(urljoin(API_BASE, f"experiences/company/{company_id}"), timeout=API_TIMEOUT)
    r.raise_for_status()
    return r.json()

def submit_experience(payload, token: str | None = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.post(urljoin(API_BASE, "experiences/submit"), json=payload, headers=headers, timeout=API_TIMEOUT)
    return r


def get_resources(token: str | None = None, category: str | None = None):
    """Get public resources (no auth required)."""
    url = urljoin(API_BASE, "content/resources")
    params = {}
    if category:
        params["category"] = category
    r = requests.get(url, params=params, timeout=API_TIMEOUT)
    r.raise_for_status()
    return r.json()


def get_resumes(token: str | None = None):
    """Get public resume samples (no auth required)."""
    r = requests.get(urljoin(API_BASE, "content/resumes"), timeout=API_TIMEOUT)
    r.raise_for_status()
    return r.json()


def get_announcements(token: str | None = None):
    """Get public announcements (no auth required)."""
    r = requests.get(urljoin(API_BASE, "content/announcements"), timeout=API_TIMEOUT)
    r.raise_for_status()
    return r.json()


def get_student_profile(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(urljoin(API_BASE, "students/me"), headers=headers, timeout=API_TIMEOUT)
    r.raise_for_status()
    return r.json()

# --- Analytics ---

def get_admin_analytics(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(urljoin(API_BASE, "analytics/admin/stats"), headers=headers, timeout=API_TIMEOUT)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}

def get_student_analytics(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(urljoin(API_BASE, "analytics/student/stats"), headers=headers, timeout=API_TIMEOUT)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}

# --- Placement Drives ---

def get_drives():
    try:
        r = requests.get(urljoin(API_BASE, "drives/"), timeout=API_TIMEOUT)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def create_drive(token, payload):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(urljoin(API_BASE, "drives/"), json=payload, headers=headers, timeout=API_TIMEOUT)

def delete_drive(token, drive_id):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.delete(urljoin(API_BASE, f"drives/{drive_id}"), headers=headers, timeout=API_TIMEOUT)

def apply_for_drive(token, drive_id):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(urljoin(API_BASE, f"drives/{drive_id}/apply"), headers=headers, timeout=API_TIMEOUT)

def get_my_applications(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(urljoin(API_BASE, "drives/my-applications"), headers=headers, timeout=API_TIMEOUT)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []
