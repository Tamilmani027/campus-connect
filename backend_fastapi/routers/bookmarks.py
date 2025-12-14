from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db
from ..models import bookmark as models
from ..models.student import Student
from ..utils.dependencies import get_current_student

router = APIRouter(
    prefix="/bookmarks",
    tags=["bookmarks"],
    responses={404: {"description": "Not found"}},
)

class BookmarkCreate(BaseModel):
    entity_type: str
    entity_id: int
    note: Optional[str] = None

class BookmarkOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    note: Optional[str]
    created_at: str
    
    class Config:
        orm_mode = True

@router.get("/", response_model=List[BookmarkOut])
def get_my_bookmarks(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    return db.query(models.Bookmark).filter(models.Bookmark.user_id == current_student.id).all()

@router.post("/")
def create_bookmark(
    bookmark: BookmarkCreate,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    # Check if already bookmarked?
    existing = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_student.id,
        models.Bookmark.entity_type == bookmark.entity_type,
        models.Bookmark.entity_id == bookmark.entity_id
    ).first()
    
    if existing:
        return {"msg": "Already bookmarked", "id": existing.id}
    
    new_bookmark = models.Bookmark(
        user_id=current_student.id,
        entity_type=bookmark.entity_type,
        entity_id=bookmark.entity_id,
        note=bookmark.note
    )
    db.add(new_bookmark)
    db.commit()
    db.refresh(new_bookmark)
    return new_bookmark

@router.delete("/{bookmark_id}")
def delete_bookmark(
    bookmark_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    bm = db.query(models.Bookmark).filter(
        models.Bookmark.id == bookmark_id,
        models.Bookmark.user_id == current_student.id
    ).first()
    
    if not bm:
        raise HTTPException(status_code=404, detail="Bookmark not found")
        
    db.delete(bm)
    db.commit()
    return {"msg": "Bookmark removed"}
