from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.interview_experience import InterviewExperience
from ..models.student import Student
from ..schemas.experience import ExperienceCreate, ExperienceOut
from ..utils.dependencies import get_current_student

router = APIRouter(prefix="/experiences", tags=["experiences"])

@router.post("/submit", response_model=ExperienceOut)
def submit_experience(payload: ExperienceCreate, db: Session = Depends(get_db), student: Student = Depends(get_current_student)):
    exp_data = payload.dict()
    exp_data["student_name"] = exp_data.get("student_name") or student.name
    exp_data["department"] = exp_data.get("department") or student.department
    exp_data["batch"] = exp_data.get("batch") or student.batch
    exp = InterviewExperience(**exp_data)
    exp.status = "pending"
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp

@router.get("/", response_model=List[ExperienceOut])
def list_approved_experiences(db: Session = Depends(get_db)):
    exps = db.query(InterviewExperience).filter(InterviewExperience.status == "approved").all()
    return exps

@router.get("/company/{company_id}", response_model=List[ExperienceOut])
def list_company_experiences(company_id: int, db: Session = Depends(get_db)):
    exps = db.query(InterviewExperience).filter(InterviewExperience.company_id == company_id, InterviewExperience.status == "approved").all()
    return exps
