from pydantic import BaseModel
from typing import Optional

class ExperienceCreate(BaseModel):
    student_name: str
    department: Optional[str] = None
    batch: Optional[int] = None
    company_id: int
    role: Optional[str] = None
    experience_text: str
    rounds: Optional[str] = None
    questions_faced: Optional[str] = None
    tips: Optional[str] = None

class ExperienceOut(ExperienceCreate):
    id: int
    status: str
    class Config:
        from_attributes = True
