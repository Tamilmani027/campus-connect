from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class CompanyHistory(Base):
    __tablename__ = "company_history"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    year = Column(Integer, nullable=False)
    role = Column(String(255), nullable=True)
    salary = Column(String(100), nullable=True)
    rounds_count = Column(Integer, default=0)
    eligibility = Column(String(255), nullable=True)

    company = relationship("Company", backref="history")
