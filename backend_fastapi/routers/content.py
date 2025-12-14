from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
try:
    from ..database import get_db
    from ..models.content import Resource, ResumeSample, Announcement
    from ..schemas.content import ResourceOut, ResumeOut, AnnouncementOut
except Exception:
    from backend_fastapi.database import get_db
    from backend_fastapi.models.content import Resource, ResumeSample, Announcement
    from backend_fastapi.schemas.content import ResourceOut, ResumeOut, AnnouncementOut


router = APIRouter(prefix="/content", tags=["content"])


@router.get("/resources", response_model=List[ResourceOut])
def public_resources(category: str = None, db: Session = Depends(get_db)):
    query = db.query(Resource)
    if category:
        query = query.filter(Resource.category == category)
    return query.order_by(Resource.created_at.desc()).all()


@router.get("/resumes", response_model=List[ResumeOut])
def public_resumes(db: Session = Depends(get_db)):
    return db.query(ResumeSample).order_by(ResumeSample.created_at.desc()).all()


@router.get("/announcements", response_model=List[AnnouncementOut])
def public_announcements(db: Session = Depends(get_db)):
    return db.query(Announcement).order_by(Announcement.created_at.desc()).all()



from fastapi import File, UploadFile, Form, HTTPException
from ..utils.dependencies import require_admin
from ..utils.file_handler import save_upload_file
from ..models.file_storage import FileStorage
import os

@router.post("/resources")
async def create_resource(
    title: str = Form(...),
    description: str = Form(None),
    url: str = Form(None),
    category: str = Form("GENERAL"),
    file: UploadFile = File(None),
    current_admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    if not url and not file:
        raise HTTPException(status_code=400, detail="Either URL or File must be provided")
        
    new_resource = Resource(
        title=title,
        description=description,
        url=url,
        category=category
    )
    
    if file:
        try:
            file_data = await save_upload_file(file, "resource")
            new_file = FileStorage(
                filename=file_data["filename"],
                original_filename=file_data["original_filename"],
                file_path=file_data["file_path"],
                file_type=file_data["file_type"],
                file_size=file_data["file_size"],
                mime_type=file_data["mime_type"],
                entity_type=file_data["entity_type"]
            )
            db.add(new_file)
            db.commit() # Commit to get ID
            db.refresh(new_file)
            
            new_resource.file_id = new_file.id
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource
