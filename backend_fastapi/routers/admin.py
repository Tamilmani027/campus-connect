from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile, Request
from sqlalchemy.orm import Session
from typing import List, Optional
try:
    from ..database import get_db
    from ..models.interview_experience import InterviewExperience
    from ..models.company import Company
    from ..models.content import Resource, ResumeSample, Announcement
    from ..models.file_storage import FileStorage
    from ..schemas.content import ResourceCreate, ResourceOut, ResumeCreate, ResumeOut, AnnouncementCreate, AnnouncementOut
    from ..utils.dependencies import require_admin
    from ..utils.file_handler import save_upload_file, delete_file
except Exception:
    from backend_fastapi.database import get_db
    from backend_fastapi.models.interview_experience import InterviewExperience
    from backend_fastapi.models.company import Company
    from backend_fastapi.models.content import Resource, ResumeSample, Announcement
    from backend_fastapi.models.file_storage import FileStorage
    from backend_fastapi.schemas.content import ResourceCreate, ResourceOut, ResumeCreate, ResumeOut, AnnouncementCreate, AnnouncementOut
    from backend_fastapi.utils.dependencies import require_admin
    from backend_fastapi.utils.file_handler import save_upload_file, delete_file

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/pending-experiences")
def pending_experiences(db: Session = Depends(get_db), _=Depends(require_admin)):
    exps = db.query(InterviewExperience).filter(InterviewExperience.status == "pending").all()
    return exps

@router.put("/approve-experience/{exp_id}")
def approve_experience(exp_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    exp = db.query(InterviewExperience).filter(InterviewExperience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    exp.status = "approved"
    db.commit()
    return {"msg": "approved"}

@router.put("/reject-experience/{exp_id}")
def reject_experience(exp_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    exp = db.query(InterviewExperience).filter(InterviewExperience.id == exp_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    exp.status = "rejected"
    db.commit()
    return {"msg": "rejected"}

# Companies management
@router.post("/companies", response_model=dict)
async def admin_create_company(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    sector: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    profile_doc: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    # Check if company exists
    existing = db.query(Company).filter(Company.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company exists")

    # Create company
    company = Company(
        name=name,
        description=description,
        website=website,
        sector=sector
    )
    db.add(company)
    db.flush()  # Get company ID without committing

    # Handle logo upload
    if logo:
        try:
            file_data = await save_upload_file(logo, "company_logos", company.id)
            file_storage = FileStorage(**file_data)
            db.add(file_storage)
            db.flush()
            company.logo_file_id = file_storage.id
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading logo: {str(e)}")

    # Handle profile document upload
    if profile_doc:
        try:
            file_data = await save_upload_file(profile_doc, "company_docs", company.id)
            file_storage = FileStorage(**file_data)
            db.add(file_storage)
            db.flush()
            company.profile_doc_id = file_storage.id
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading profile document: {str(e)}")

    db.commit()
    db.refresh(company)
    return {"id": company.id, "msg": "created"}

@router.put("/companies/{company_id}", response_model=dict)
def admin_update_company(company_id: int, payload: dict, db: Session = Depends(get_db), _=Depends(require_admin)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for k, v in payload.items():
        if hasattr(company, k):
            setattr(company, k, v)
    db.commit()
    return {"msg": "updated"}

@router.delete("/companies/{company_id}", response_model=dict)
def admin_delete_company(company_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()
    return {"msg": "deleted"}

# Resources
@router.post("/resources", response_model=ResourceOut)
async def create_resource(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    if not url and not file:
        raise HTTPException(status_code=400, detail="Either URL or file is required")

    resource = Resource(
        title=title,
        description=description,
        url=url
    )
    db.add(resource)
    db.flush()

    if file:
        try:
            file_data = await save_upload_file(file, "resources", resource.id)
            file_storage = FileStorage(**file_data)
            db.add(file_storage)
            db.flush()
            resource.file_id = file_storage.id
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

    db.commit()
    db.refresh(resource)
    return resource

@router.get("/resources", response_model=list[ResourceOut])
def list_resources(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(Resource).all()

@router.delete("/resources/{rid}", response_model=dict)
def delete_resource(rid: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    r = db.query(Resource).filter(Resource.id == rid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(r)
    db.commit()
    return {"msg": "deleted"}


@router.put("/resources/{rid}", response_model=ResourceOut)
def update_resource(rid: int, payload: ResourceCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    r = db.query(Resource).filter(Resource.id == rid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    resource_data = payload.dict()
    resource_data["url"] = str(resource_data["url"])
    for field, value in resource_data.items():
        setattr(r, field, value)
    db.commit()
    db.refresh(r)
    return r

# Resumes
@router.post("/resumes", response_model=ResumeOut)
async def create_resume(
    title: str = Form(...),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    if not url and not file:
        raise HTTPException(status_code=400, detail="Either URL or file is required")

    resume = ResumeSample(
        title=title,
        url=url
    )
    db.add(resume)
    db.flush()

    if file:
        try:
            file_data = await save_upload_file(file, "resumes", resume.id)
            file_storage = FileStorage(**file_data)
            db.add(file_storage)
            db.flush()
            resume.file_id = file_storage.id
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

    db.commit()
    db.refresh(resume)
    return resume

@router.get("/resumes", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(ResumeSample).all()

@router.delete("/resumes/{rid}", response_model=dict)
def delete_resume(rid: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    r = db.query(ResumeSample).filter(ResumeSample.id == rid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(r)
    db.commit()
    return {"msg": "deleted"}


@router.put("/resumes/{rid}", response_model=ResumeOut)
def update_resume(rid: int, payload: ResumeCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    r = db.query(ResumeSample).filter(ResumeSample.id == rid).first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    resume_data = payload.dict()
    resume_data["url"] = str(resume_data["url"])
    for field, value in resume_data.items():
        setattr(r, field, value)
    db.commit()
    db.refresh(r)
    return r

# Announcements
@router.post("/announcements", response_model=AnnouncementOut)
async def create_announcement(
    request: Request,
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    """
    Accept either JSON (application/json) with {title, content} or multipart/form-data
    with form fields `title`, `content` and optional file upload `file`.
    """
    content_type = request.headers.get("content-type", "")
    title = None
    content = None

    if "application/json" in content_type:
        body = await request.json()
        title = body.get("title")
        content = body.get("content")
    else:
        # multipart/form-data or other form encodings
        form = await request.form()
        title = form.get("title")
        content = form.get("content")
        # if file wasn't injected by FastAPI param, try to get from form
        if not file:
            maybe_file = form.get("file")
            if maybe_file is not None:
                file = maybe_file

    if not title or not content:
        raise HTTPException(status_code=422, detail="title and content are required")

    announcement = Announcement(
        title=title,
        content=content
    )
    db.add(announcement)
    db.flush()

    if file:
        try:
            file_data = await save_upload_file(file, "announcements", announcement.id)
            file_storage = FileStorage(**file_data)
            db.add(file_storage)
            db.flush()
            announcement.file_id = file_storage.id
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

    db.commit()
    db.refresh(announcement)
    return announcement

@router.get("/announcements", response_model=list[AnnouncementOut])
def list_announcements(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(Announcement).order_by(Announcement.created_at.desc()).all()

@router.delete("/announcements/{aid}", response_model=dict)
def delete_announcement(aid: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    a = db.query(Announcement).filter(Announcement.id == aid).first()
    if not a:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(a)
    db.commit()
    return {"msg": "deleted"}


@router.put("/announcements/{aid}", response_model=AnnouncementOut)
def update_announcement(aid: int, payload: AnnouncementCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    a = db.query(Announcement).filter(Announcement.id == aid).first()
    if not a:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in payload.dict().items():
        setattr(a, field, value)
    db.commit()
    db.refresh(a)
    return a
