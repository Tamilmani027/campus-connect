from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ForumThread(Base):
    __tablename__ = "forum_threads"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String(200), nullable=True) # e.g. "DSA, Arrays"
    views = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    replies = relationship("ForumReply", back_populates="thread", cascade="all, delete-orphan")
    # Assuming Student model will need 'threads' relationship or we just keep it one-way here for now

class ForumReply(Base):
    __tablename__ = "forum_replies"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("forum_threads.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True) # Null if admin/system
    admin_id = Column(Integer, nullable=True) # If we had an Admin model table, we'd link it. For now just ID.
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    thread = relationship("ForumThread", back_populates="replies")
