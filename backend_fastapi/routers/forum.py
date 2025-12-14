from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..database import get_db
from ..models import discussion as models
from ..models.student import Student
from ..models.admin import Admin
from ..utils.dependencies import get_current_student, get_current_admin_or_student, get_current_user_id_and_role

router = APIRouter(
    prefix="/forum",
    tags=["forum"],
    responses={404: {"description": "Not found"}},
)

# --- Schemas ---
class ReplyOut(BaseModel):
    id: int
    content: str
    student_id: Optional[int]
    admin_id: Optional[int]
    created_at: datetime
    
    class Config:
        orm_mode = True

class ThreadOut(BaseModel):
    id: int
    title: str
    content: str
    tags: Optional[str]
    views: int
    created_at: datetime
    student_id: int
    replies: List[ReplyOut] = []
    
    class Config:
        orm_mode = True

class ThreadCreate(BaseModel):
    title: str
    content: str
    tags: Optional[str] = None

class ReplyCreate(BaseModel):
    content: str


# --- Routes ---

@router.get("/", response_model=List[ThreadOut])
def get_threads(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    threads = db.query(models.ForumThread).order_by(models.ForumThread.created_at.desc()).offset(skip).limit(limit).all()
    return threads

@router.post("/", response_model=ThreadOut)
def create_thread(
    thread: ThreadCreate,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    new_thread = models.ForumThread(
        title=thread.title,
        content=thread.content,
        tags=thread.tags,
        student_id=current_student.id
    )
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)
    return new_thread

@router.get("/{thread_id}", response_model=ThreadOut)
def get_thread(thread_id: int, db: Session = Depends(get_db)):
    thread = db.query(models.ForumThread).filter(models.ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Increment view count
    thread.views += 1
    db.commit()
    
    return thread

@router.post("/{thread_id}/reply")
def reply_to_thread(
    thread_id: int,
    reply: ReplyCreate,
    user_info = Depends(get_current_user_id_and_role), # Custom dependency to allow both students and admins
    db: Session = Depends(get_db)
):
    user_id, role = user_info
    
    thread = db.query(models.ForumThread).filter(models.ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    new_reply = models.ForumReply(
        thread_id=thread_id,
        content=reply.content,
        student_id=user_id if role == 'student' else None,
        admin_id=user_id if role == 'admin' else None
    )
    
    db.add(new_reply)
    db.commit()
    db.refresh(new_reply)
    return {"msg": "Reply added", "id": new_reply.id}
