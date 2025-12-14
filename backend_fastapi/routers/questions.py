from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import question as models
from ..schemas import question as schemas
from ..utils.dependencies import get_current_student as get_current_active_student, require_admin as get_current_admin
from ..models.student import Student

router = APIRouter(
    prefix="/questions",
    tags=["questions"],
    responses={404: {"description": "Not found"}},
)

# --- Public / Student Routes ---

@router.get("/", response_model=List[schemas.QuestionOut])
def get_questions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    type: Optional[schemas.QuestionTypeEnum] = None,
    difficulty: Optional[schemas.DifficultyEnum] = None,
    topic: Optional[str] = None
):
    query = db.query(models.Question)
    if type:
        query = query.filter(models.Question.type == type.value)
    if difficulty:
        query = query.filter(models.Question.difficulty == difficulty.value)
    if topic:
        query = query.filter(models.Question.topic.ilike(f"%{topic}%"))
    
    return query.offset(skip).limit(limit).all()

@router.get("/{question_id}", response_model=schemas.QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.get("/{question_id}/progress", response_model=schemas.UserProgressOut)
def get_question_progress(
    question_id: int,
    current_student: Student = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    progress = db.query(models.UserProgress).filter(
        models.UserProgress.question_id == question_id,
        models.UserProgress.student_id == current_student.id
    ).first()
    
    if not progress:
        # Return empty progress or default
        return schemas.UserProgressOut(
            id=0, student_id=current_student.id, question_id=question_id, 
            status="NOT_STARTED", updated_at=None
        )
    return progress

@router.post("/{question_id}/progress")
def update_progress(
    question_id: int,
    progress_data: schemas.UserProgressUpdate,
    current_student: Student = Depends(get_current_active_student),
    db: Session = Depends(get_db)
):
    # Check if question exists
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    progress = db.query(models.UserProgress).filter(
        models.UserProgress.question_id == question_id,
        models.UserProgress.student_id == current_student.id
    ).first()
    
    if not progress:
        progress = models.UserProgress(
            student_id=current_student.id,
            question_id=question_id,
            status=progress_data.status,
            submission_code=progress_data.submission_code,
            user_notes=progress_data.user_notes,
            is_bookmarked=progress_data.is_bookmarked
        )
        db.add(progress)
    else:
        if progress_data.status:
            progress.status = progress_data.status
        if progress_data.submission_code is not None:
            progress.submission_code = progress_data.submission_code
        if progress_data.user_notes is not None:
            progress.user_notes = progress_data.user_notes
        if progress_data.is_bookmarked is not None:
            progress.is_bookmarked = progress_data.is_bookmarked
            
    db.commit()
    db.refresh(progress)
    return {"status": "success", "progress_id": progress.id}

# --- Admin Routes ---

@router.post("/", response_model=schemas.QuestionOut)
def create_question(
    question: schemas.QuestionCreate,
    current_admin=Depends(get_current_admin), # Assuming admin check returns admin user or True
    db: Session = Depends(get_db)
):
    new_question = models.Question(
        title=question.title,
        description=question.description,
        type=question.type.value,
        difficulty=question.difficulty.value,
        topic=question.topic,
        company_tags=question.company_tags,
        options=question.options,
        correct_option=question.correct_option,
        solution=question.solution,
        test_cases=question.test_cases
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    return {"status": "deleted"}
