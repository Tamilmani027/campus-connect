from sqlalchemy import Column, Integer, String, Text
from ..database import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    sector = Column(String(100), nullable=True)
