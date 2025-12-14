from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.placement_drive import PlacementDrive
from ..models.student_application import StudentApplication
from ..models.student import Student
from ..models.company import Company
from ..utils.dependencies import require_admin, get_current_student
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/drives", tags=["drives"])

# Schemas (Simplified for speed, ideally in schemas folder)
class DriveCreate(BaseModel):
    company_id: int
    batch: int
    role: str
    description: Optional[str] = None
    date: datetime
    deadline: datetime
    eligibility_criteria: Optional[str] = None

class DriveOut(DriveCreate):
    id: int
    status: str
    created_at: datetime
    company_name: str # enriched field

    class Config:
        orm_mode = True

# --- Admin Endpoints ---

@router.post("/", response_model=dict)
def create_drive(drive: DriveCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    new_drive = PlacementDrive(**drive.dict())
    db.add(new_drive)
    db.commit()
    db.refresh(new_drive)
    return {"msg": "created", "id": new_drive.id}

@router.delete("/{drive_id}")
def delete_drive(drive_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    drive = db.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")
    db.delete(drive)
    db.commit()
    return {"msg": "deleted"}

# --- Public/Student Endpoints ---

@router.get("/", response_model=List[DriveOut])
def list_drives(db: Session = Depends(get_db)):
    drives = db.query(PlacementDrive).filter(PlacementDrive.status == "open").order_by(PlacementDrive.deadline).all()
    # Enrich with company name
    results = []
    for d in drives:
        d_dict = d.__dict__
        if d.company:
            d_dict["company_name"] = d.company.name
        else:
            d_dict["company_name"] = "Unknown"
        results.append(d_dict)
    return results

@router.post("/{drive_id}/apply")
def apply_for_drive(drive_id: int, current_student: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    # Check if drive exists and is open
    drive = db.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if not drive or drive.status != "open":
        raise HTTPException(status_code=400, detail="Drive not available")
    
    if drive.deadline < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Deadline passed")

    # Check already applied
    existing = db.query(StudentApplication).filter(
        StudentApplication.student_id == current_student.id,
        StudentApplication.drive_id == drive_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already applied")

    app = StudentApplication(student_id=current_student.id, drive_id=drive_id)
    db.add(app)
    db.commit()
    return {"msg": "applied"}

@router.get("/my-applications")
def my_applications(current_student: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    apps = db.query(StudentApplication).filter(StudentApplication.student_id == current_student.id).all()
    # Enrich details
    results = []
    for app in apps:
        drive = app.drive
        res = {
            "id": app.id,
            "status": app.status,
            "applied_at": app.applied_at,
            "company_name": drive.company.name if drive and drive.company else "Unknown",
            "role": drive.role if drive else "Unknown",
            "drive_date": drive.date if drive else None
        }
        results.append(res)
    return results
