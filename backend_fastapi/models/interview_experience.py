from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref
from ..database import Base

class InterviewExperience(Base):
    __tablename__ = "interview_experiences"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=True)
    batch = Column(Integer, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    role = Column(String(255), nullable=True)
    experience_text = Column(Text, nullable=False)
    rounds = Column(String(1000), nullable=True)
    questions_faced = Column(String(2000), nullable=True)
    tips = Column(String(1000), nullable=True)
    status = Column(String(50), default="pending")  # pending/approved/rejected

    company = relationship("Company", backref=backref("experiences", cascade="all, delete-orphan"))
