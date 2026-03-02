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


from fastapi.responses import FileResponse
import os
from pathlib import Path

@router.get("/file/{file_id}")
async def download_file(file_id: int, db: Session = Depends(get_db)):
    """Download a file by ID (public access for students and admins)."""
    file_record = db.query(FileStorage).filter(FileStorage.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = Path(file_record.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File does not exist on disk")
    
    return FileResponse(
        path=file_path,
        filename=file_record.original_filename,
        media_type=file_record.mime_type
    )

@router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: int,
    current_admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a resource by ID (admin only)."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Delete associated file if it exists
    if resource.file_id:
        file_record = db.query(FileStorage).filter(FileStorage.id == resource.file_id).first()
        if file_record:
            try:
                file_path = Path(file_record.file_path)
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                print(f"Error deleting file: {str(e)}")
            db.delete(file_record)
    
    db.delete(resource)
    db.commit()
    return {"message": "Resource deleted successfully"}

@router.put("/resources/{resource_id}")
async def update_resource(
    resource_id: int,
    title: str = Form(None),
    description: str = Form(None),
    url: str = Form(None),
    file: UploadFile = File(None),
    current_admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a resource by ID (admin only)."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Update fields if provided
    if title:
        resource.title = title
    if description:
        resource.description = description
    if url:
        resource.url = url
    
    # Handle file update
    if file and file.filename:
        try:
            # Delete old file if exists
            if resource.file_id:
                old_file = db.query(FileStorage).filter(FileStorage.id == resource.file_id).first()
                if old_file:
                    try:
                        old_path = Path(old_file.file_path)
                        if old_path.exists():
                            old_path.unlink()
                    except Exception:
                        pass
                    db.delete(old_file)
            
            # Save new file
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
            db.commit()
            db.refresh(new_file)
            resource.file_id = new_file.id
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    db.commit()
    db.refresh(resource)
    return resource
