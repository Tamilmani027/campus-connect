import requests
from urllib.parse import urljoin
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE", "http://localhost:8000/")

def get_companies():
    r = requests.get(urljoin(API_BASE, "companies/"))
    r.raise_for_status()
    return r.json()

def get_company(company_id):
    r = requests.get(urljoin(API_BASE, f"companies/{company_id}"))
    r.raise_for_status()
    return r.json()

def get_company_experiences(company_id):
    r = requests.get(urljoin(API_BASE, f"experiences/company/{company_id}"))
    r.raise_for_status()
    return r.json()

def submit_experience(payload, token: str | None = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.post(urljoin(API_BASE, "experiences/submit"), json=payload, headers=headers)
    return r
