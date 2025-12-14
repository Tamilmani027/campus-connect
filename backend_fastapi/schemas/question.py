from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class QuestionTypeEnum(str, Enum):
    CODING = "CODING"
    APTITUDE = "APTITUDE"
    HR = "HR"

class DifficultyEnum(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class QuestionBase(BaseModel):
    title: str
    description: str
    type: QuestionTypeEnum
    difficulty: DifficultyEnum
    topic: Optional[str] = None
    company_tags: Optional[str] = None
    options: Optional[Dict[str, str]] = None
    correct_option: Optional[str] = None
    solution: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(QuestionBase):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[QuestionTypeEnum] = None
    difficulty: Optional[DifficultyEnum] = None

class QuestionOut(QuestionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserProgressBase(BaseModel):
    status: str
    submission_code: Optional[str] = None
    user_notes: Optional[str] = None
    is_bookmarked: Optional[bool] = False

class UserProgressUpdate(UserProgressBase):
    pass

class UserProgressOut(UserProgressBase):
    id: int
    student_id: int
    question_id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True
