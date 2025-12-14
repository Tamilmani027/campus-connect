from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date, Enum
from sqlalchemy.orm import relationship, backref
from ..database import Base
from datetime import datetime

class PlacementDrive(Base):
    __tablename__ = "placement_drives"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    batch = Column(Integer, nullable=False)  # e.g., 2025
    role = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=False)  # Interview/Drive date
    deadline = Column(DateTime, nullable=False)  # Application deadline
    eligibility_criteria = Column(Text, nullable=True)
    status = Column(String(50), default="open")  # open, closed, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", backref=backref("drives", cascade="all, delete-orphan"))
