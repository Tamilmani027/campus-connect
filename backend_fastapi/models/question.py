from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class QuestionType(str, enum.Enum):
    CODING = "CODING"
    APTITUDE = "APTITUDE"
    HR = "HR"

class DifficultyLevel(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String(50), nullable=False) # stored as string, validated by schema
    difficulty = Column(String(50), nullable=False, default="MEDIUM")
    topic = Column(String(100), nullable=True) # e.g. "Arrays", "Verbal"
    company_tags = Column(String(500), nullable=True) # Comma-separated or JSON string
    
    # For Aptitude
    options = Column(JSON, nullable=True) # {"A": "val", "B": "val"}
    correct_option = Column(String(5), nullable=True) # "A"
    
    # For Coding / General
    solution = Column(Text, nullable=True)
    test_cases = Column(JSON, nullable=True) # [{"input": "...", "output": "..."}]
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    progress = relationship("UserProgress", back_populates="question")

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    
    status = Column(String(20), default="ATTEMPTED") # SOLVED, ATTEMPTED
    submission_code = Column(Text, nullable=True)
    user_notes = Column(Text, nullable=True)
    is_bookmarked = Column(Boolean, default=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    question = relationship("Question", back_populates="progress")
    # Assuming Student model has relationship 'progress' or we add it there, 
    # but for now we define the foreign key.
