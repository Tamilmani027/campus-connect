from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

class DailyTaskBase(BaseModel):
    day_number: int
    title: str
    description: Optional[str] = None
    reference_link: Optional[str] = None

class DailyTaskCreate(DailyTaskBase):
    pass

class DailyTaskOut(DailyTaskBase):
    id: int
    plan_id: int

    class Config:
        from_attributes = True

class StudyPlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_days: int

class StudyPlanCreate(StudyPlanBase):
    pass

class StudyPlanOut(StudyPlanBase):
    id: int
    created_at: datetime
    tasks: List[DailyTaskOut] = []

    class Config:
        from_attributes = True

class SubscriptionOut(BaseModel):
    id: int
    student_id: int
    plan_id: int
    start_date: datetime
    current_day: int
    is_active: bool
    plan: StudyPlanOut
    completed_tasks_list: List[int] = [] # Computed field

    class Config:
        from_attributes = True
