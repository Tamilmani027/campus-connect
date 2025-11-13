from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.content import Resource, ResumeSample, Announcement
from ..schemas.content import ResourceOut, ResumeOut, AnnouncementOut


router = APIRouter(prefix="/content", tags=["content"])


@router.get("/resources", response_model=List[ResourceOut])
def public_resources(db: Session = Depends(get_db)):
    return db.query(Resource).order_by(Resource.created_at.desc()).all()


@router.get("/resumes", response_model=List[ResumeOut])
def public_resumes(db: Session = Depends(get_db)):
    return db.query(ResumeSample).order_by(ResumeSample.created_at.desc()).all()


@router.get("/announcements", response_model=List[AnnouncementOut])
def public_announcements(db: Session = Depends(get_db)):
    return db.query(Announcement).order_by(Announcement.created_at.desc()).all()


