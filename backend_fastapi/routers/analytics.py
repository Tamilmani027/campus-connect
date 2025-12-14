from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models.company import Company
from ..models.student import Student
from ..models.interview_experience import InterviewExperience
from ..models.student_application import StudentApplication
from ..models.placement_drive import PlacementDrive
from ..utils.dependencies import require_admin, get_current_student

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/admin/stats")
def admin_stats(db: Session = Depends(get_db), _=Depends(require_admin)):
    # 1. Company Sector Distribution
    sector_data = db.query(Company.sector, func.count(Company.id)).group_by(Company.sector).all()
    sectors = [{"label": s[0] or "Unknown", "count": s[1]} for s in sector_data]
    
    # 2. Application Status Distribution
    status_data = db.query(StudentApplication.status, func.count(StudentApplication.id)).group_by(StudentApplication.status).all()
    app_status = [{"label": s[0], "count": s[1]} for s in status_data]
    
    # 3. Overall Placement Trends (Mock data for now as we don't have historical placement tables fully populated)
    # Ideally this would query a 'PlacementResult' table
    trends = [
        {"year": 2023, "placed": 150},
        {"year": 2024, "placed": 200},
        {"year": 2025, "placed": 50}  # Current year
    ]
    
    return {
        "sectors": sectors,
        "application_status": app_status,
        "trends": trends
    }

@router.get("/student/stats")
def student_stats(current_user: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    # 1. My Applications Status
    my_status_data = db.query(StudentApplication.status, func.count(StudentApplication.id))\
        .filter(StudentApplication.student_id == current_user.id)\
        .group_by(StudentApplication.status).all()
    my_status = [{"label": s[0], "count": s[1]} for s in my_status_data]
    
    # 2. Upcoming Drives Count
    import datetime
    upcoming_count = db.query(PlacementDrive).filter(PlacementDrive.deadline >= datetime.datetime.utcnow()).count()
    
    return {
        "my_status": my_status,
        "upcoming_drives": upcoming_count
    }
