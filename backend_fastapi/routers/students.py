from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..models.student import Student
from ..schemas.student import StudentRegister, StudentLogin, StudentOut
from ..schemas.auth import Token
from ..utils.hashing import hash_password, verify_password
from ..utils.jwt_handler import create_access_token
from ..utils.dependencies import get_current_student
from ..config import settings

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/register", response_model=StudentOut)
def register_student(payload: StudentRegister, db: Session = Depends(get_db)):
	existing = db.query(Student).filter(Student.email == payload.email).first()
	if existing:
		raise HTTPException(status_code=400, detail="Email already registered")
	student = Student(
		name=payload.name,
		email=payload.email,
		department=payload.department,
		batch=payload.batch,
		password_hash=hash_password(payload.password)
	)
	db.add(student)
	db.commit()
	db.refresh(student)
	return student

@router.post("/login", response_model=Token)
def student_login(payload: StudentLogin, db: Session = Depends(get_db)):
	student = db.query(Student).filter(Student.email == payload.email).first()
	if not student or not verify_password(payload.password, student.password_hash):
		raise HTTPException(status_code=401, detail="Invalid credentials")
	expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	token = create_access_token({"sub": student.email, "role": "student", "sid": student.id}, expires)
	return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=StudentOut)
def student_me(current_student: Student = Depends(get_current_student)):
    return current_student


