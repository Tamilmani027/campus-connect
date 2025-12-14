from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("students.id"), nullable=False) # Assuming mostly students
    entity_type = Column(String(50), nullable=False) # 'interview_experience', 'question', 'resource'
    entity_id = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships can be tricky with polymorphic-like associations.
    # We might fetch related entities manually or define explicit secondary relationships if needed.
