from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from models.admin import Admin
from schemas.auth import Token, AdminAuth
from utils.hashing import hash_password, verify_password
from utils.jwt_handler import create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

# Simple endpoint to create initial admin (only for development)
@router.post("/create-admin", response_model=dict)
def create_admin(payload: AdminAuth, db: Session = Depends(get_db)):
    existing = db.query(Admin).filter(Admin.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin exists")
    admin = Admin(username=payload.username, password_hash=hash_password(payload.password))
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return {"msg": "admin created"}

@router.post("/login", response_model=Token)
def login(payload: AdminAuth, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == payload.username).first()
    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": admin.username, "role": "admin", "aid": admin.id}, expires_delta=timedelta(hours=24))
    return {"access_token": access_token, "token_type": "bearer"}
