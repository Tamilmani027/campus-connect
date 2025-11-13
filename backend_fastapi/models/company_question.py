from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class CompanyQuestion(Base):
    __tablename__ = "company_questions"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    question = Column(String(2000), nullable=False)
    category = Column(String(50), nullable=False)  # aptitude/coding/technical/hr
    difficulty = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)

    company = relationship("Company", backref="questions")
