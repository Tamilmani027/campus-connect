from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from ..database import Base
from datetime import datetime

class StudentApplication(Base):
    __tablename__ = "student_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    drive_id = Column(Integer, ForeignKey("placement_drives.id"), nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="applied")  # applied, shortlisted, rejected, offered
    
    student = relationship("Student", backref=backref("applications", cascade="all, delete-orphan"))
    drive = relationship("PlacementDrive", backref=backref("applications", cascade="all, delete-orphan"))
