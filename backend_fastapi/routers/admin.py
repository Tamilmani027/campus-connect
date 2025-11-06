from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.interview_experience import InterviewExperience
from ..models.company import Company
from ..models.content import Resource, ResumeSample, Announcement
from ..schemas.content import ResourceCreate, ResourceOut, ResumeCreate, ResumeOut, AnnouncementCreate, AnnouncementOut
from ..utils.jwt_handler import verify_token

router = APIRouter(prefix="/admin", tags=["admin"])

def admin_required(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing auth header")
    token = authorization.split(" ")[1] if " " in authorization else authorization
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    # subject holds admin username
    return payload.get("sub")

@router.get("/pending-experiences")
def pending_experiences(db: Session = Depends(get_db), _=Depends(admin_required)):
    exps = db.query(InterviewExperience).filter(InterviewExperience.status == "pending").all()
    return exps

@router.put("/approve-experience/{exp_id}")
def approve_experience(exp_id: int, db: Session = Depends(get_db), _=Depends(admin_required)):
    exp = db.query(InterviewExperience).filter(InterviewExperience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    exp.status = "approved"
    db.commit()
    return {"msg": "approved"}

@router.put("/reject-experience/{exp_id}")
def reject_experience(exp_id: int, db: Session = Depends(get_db), _=Depends(admin_required)):
    exp = db.query(InterviewExperience).filter(InterviewExperience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    exp.status = "rejected"
    db.commit()
    return {"msg": "rejected"}

# Companies management
@router.post("/companies", response_model=dict)
def admin_create_company(payload: dict, db: Session = Depends(get_db), _=Depends(admin_required)):
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="name required")
    existing = db.query(Company).filter(Company.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company exists")
    company = Company(**payload)
    db.add(company)
    db.commit()
    db.refresh(company)
    return {"id": company.id, "msg": "created"}

@router.put("/companies/{company_id}", response_model=dict)
def admin_update_company(company_id: int, payload: dict, db: Session = Depends(get_db), _=Depends(admin_required)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for k, v in payload.items():
        if hasattr(company, k):
            setattr(company, k, v)
    db.commit()
    return {"msg": "updated"}

@router.delete("/companies/{company_id}", response_model=dict)
def admin_delete_company(company_id: int, db: Session = Depends(get_db), _=Depends(admin_required)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()
    return {"msg": "deleted"}

# Resources
@router.post("/resources", response_model=ResourceOut)
def create_resource(payload: ResourceCreate, db: Session = Depends(get_db), _=Depends(admin_required)):
    r = Resource(**payload.dict())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.get("/resources", response_model=list[ResourceOut])
def list_resources(db: Session = Depends(get_db), _=Depends(admin_required)):
    return db.query(Resource).all()

@router.delete("/resources/{rid}", response_model=dict)
def delete_resource(rid: int, db: Session = Depends(get_db), _=Depends(admin_required)):
    r = db.query(Resource).filter(Resource.id == rid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(r)
    db.commit()
    return {"msg": "deleted"}

# Resumes
@router.post("/resumes", response_model=ResumeOut)
def create_resume(payload: ResumeCreate, db: Session = Depends(get_db), _=Depends(admin_required)):
    r = ResumeSample(**payload.dict())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.get("/resumes", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db), _=Depends(admin_required)):
    return db.query(ResumeSample).all()

@router.delete("/resumes/{rid}", response_model=dict)
def delete_resume(rid: int, db: Session = Depends(get_db), _=Depends(admin_required)):
    r = db.query(ResumeSample).filter(ResumeSample.id == rid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(r)
    db.commit()
    return {"msg": "deleted"}

# Announcements
@router.post("/announcements", response_model=AnnouncementOut)
def create_announcement(payload: AnnouncementCreate, db: Session = Depends(get_db), _=Depends(admin_required)):
    a = Announcement(**payload.dict())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a

@router.get("/announcements", response_model=list[AnnouncementOut])
def list_announcements(db: Session = Depends(get_db), _=Depends(admin_required)):
    return db.query(Announcement).order_by(Announcement.created_at.desc()).all()

@router.delete("/announcements/{aid}", response_model=dict)
def delete_announcement(aid: int, db: Session = Depends(get_db), _=Depends(admin_required)):
    a = db.query(Announcement).filter(Announcement.id == aid).first()
    if not a:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(a)
    db.commit()
    return {"msg": "deleted"}
