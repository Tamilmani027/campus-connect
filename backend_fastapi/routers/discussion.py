from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from ..database import get_db
from ..models import discussion as models
from ..models.student import Student
from ..schemas import discussion as schemas
from ..utils.dependencies import get_current_student, get_current_user_id_and_role

router = APIRouter(
    prefix="/discussion",
    tags=["discussion"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.ForumThreadOut])
def get_threads(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    tag: Optional[str] = None
):
    query = db.query(models.ForumThread)
    if tag:
        query = query.filter(models.ForumThread.tags.ilike(f"%{tag}%"))
    
    threads = query.order_by(models.ForumThread.created_at.desc()).offset(skip).limit(limit).all()
    
    # Populate student names manually or via join if we had relationships set up perfectly
    # For now, simple logic
    results = []
    for t in threads:
        st = db.query(Student).filter(Student.id == t.student_id).first()
        t.student_name = st.name if st else "Unknown"
        # We don't load replies here to keep list lightweight
        t.replies = [] 
        results.append(t)
        
    return results

@router.post("/", response_model=schemas.ForumThreadOut)
def create_thread(
    thread: schemas.ForumThreadCreate,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    new_thread = models.ForumThread(
        student_id=current_student.id,
        title=thread.title,
        content=thread.content,
        tags=thread.tags
    )
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)
    new_thread.student_name = current_student.name
    return new_thread

@router.get("/{thread_id}", response_model=schemas.ForumThreadOut)
def get_thread_detail(
    thread_id: int, 
    db: Session = Depends(get_db)
):
    # Eager load replies
    thread = db.query(models.ForumThread).filter(models.ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
        
    # Increment view count
    thread.views += 1
    db.commit()
    
    # Get author name
    st = db.query(Student).filter(Student.id == thread.student_id).first()
    thread.student_name = st.name if st else "Unknown"
    
    # Enhance replies with names
    for r in thread.replies:
        if r.student_id:
            rst = db.query(Student).filter(Student.id == r.student_id).first()
            r.student_name = rst.name if rst else "Unknown"
        else:
            r.student_name = "Admin" # Placeholder for admin replies
            
    return thread

@router.post("/{thread_id}/reply", response_model=schemas.ForumReplyOut)
def post_reply(
    thread_id: int,
    reply: schemas.ForumReplyCreate,
    user_info = Depends(get_current_user_id_and_role),
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
    
    # Set display name
    if role == 'student':
        st = db.query(Student).filter(Student.id == user_id).first()
        new_reply.student_name = st.name if st else "Student"
    else:
        new_reply.student_name = "Admin"
        
    return new_reply
