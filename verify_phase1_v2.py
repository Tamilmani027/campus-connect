import requests
import sys
import os
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

def verify():
    # 1. Login as Admin
    # Create admin if not exists (idempotent-ish)
    requests.post(f"{API_BASE}/auth/create-admin", json={"username": "testadmin2", "password": "password"})
    
    s = requests.Session()
    r = s.post(f"{API_BASE}/auth/login", json={"username": "testadmin2", "password": "password"})
    if r.status_code != 200:
        print(f"Failed to login as admin: {r.text}")
        return
    admin_token = r.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("Admin Login Success")

    # 2. Check Admin Analytics
    r = s.get(f"{API_BASE}/analytics/admin/stats", headers=admin_headers)
    print(f"Admin Analytics: {r.status_code}")
    if r.status_code != 200:
        print("FAILED: Admin Analytics")

    # 3. Create a Drive
    deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
    
    # Get a company
    comps = s.get(f"{API_BASE}/companies").json()
    if not comps:
        s.post(f"{API_BASE}/admin/companies", data={"name": "AnalyticsCorp2", "sector": "IT"}, headers=admin_headers)
        comps = s.get(f"{API_BASE}/companies").json()
    
    drive_data = {
        "company_id": comps[0]["id"],
        "batch": 2025,
        "role": "SDE Test 2",
        "date": deadline,
        "deadline": deadline,
        "description": "Test Drive 2",
        "eligibility_criteria": "None"
    }
    
    r = s.post(f"{API_BASE}/drives/", json=drive_data, headers=admin_headers)
    print(f"Create Drive: {r.status_code}")
    if r.status_code == 200:
        drive_id = r.json()["id"]
    else:
        print(f"FAILED: Create Drive {r.text}")
        return

    # 4. Login as Student
    email = "analytics_student2@test.com"
    requests.post(f"{API_BASE}/students/register", json={
        "name": "Analytics Student 2", 
        "email": email, 
        "password": "password",
        "department": "CSE",
        "batch": 2025
    })
    r = s.post(f"{API_BASE}/students/login", json={"email": email, "password": "password"})
    if r.status_code != 200:
        print(f"Failed to login as student: {r.text}")
        return
    student_token = r.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    print("Student Login Success")

    # 5. List Drives (Public/Student)
    r = s.get(f"{API_BASE}/drives/")
    print(f"List Drives: {r.status_code}")
    drives = r.json()
    found = any(d["id"] == drive_id for d in drives)
    print(f"Drive Found in List: {found}")

    # 6. Apply for Drive
    r = s.post(f"{API_BASE}/drives/{drive_id}/apply", headers=student_headers)
    print(f"Apply Drive: {r.status_code} - {r.json()}")

    # 7. Check Student Analytics (My Status)
    r = s.get(f"{API_BASE}/drives/my-applications", headers=student_headers)
    print(f"My Applications: {r.status_code} - Apps count: {len(r.json())}")
    
    r = s.get(f"{API_BASE}/analytics/student/stats", headers=student_headers)
    print(f"Student Analytics: {r.status_code} - {r.json()}")


if __name__ == "__main__":
    verify()
