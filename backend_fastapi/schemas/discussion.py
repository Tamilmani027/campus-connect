from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ForumReplyBase(BaseModel):
    content: str
    admin_id: Optional[int] = None

class ForumReplyCreate(ForumReplyBase):
    pass

class ForumReplyOut(ForumReplyBase):
    id: int
    thread_id: int
    student_id: Optional[int]
    created_at: datetime
    # We might want to fetch student name too, but sticking to basic fields first
    student_name: Optional[str] = None 

    class Config:
        from_attributes = True

class ForumThreadBase(BaseModel):
    title: str
    content: str
    tags: Optional[str] = None

class ForumThreadCreate(ForumThreadBase):
    pass

class ForumThreadOut(ForumThreadBase):
    id: int
    student_id: int
    views: int
    created_at: datetime
    replies: List[ForumReplyOut] = []
    student_name: Optional[str] = None

    class Config:
        from_attributes = True
