from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base

class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    duration_days = Column(Integer, nullable=False) # e.g. 30 days
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    tasks = relationship("DailyTask", back_populates="plan", cascade="all, delete-orphan")

class DailyTask(Base):
    __tablename__ = "daily_tasks"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("study_plans.id"), nullable=False)
    day_number = Column(Integer, nullable=False) # Day 1, Day 2...
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    reference_link = Column(String(500), nullable=True) # Optional link to resource/question
    
    plan = relationship("StudyPlan", back_populates="tasks")

class StudentSubscription(Base):
    __tablename__ = "student_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("study_plans.id"), nullable=False)
    start_date = Column(DateTime, server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True)
    current_day = Column(Integer, default=1) # Track which day the student is on
    
    # We could track individual task completion here or in a separate table.
    # For simplicity, let's say "current_day" implies all tasks before that day are done,
    # or we can add a completed_tasks JSON column if we want granular tracking.
    completed_tasks = Column(Text, default="[]") # JSON list of task IDs completed
