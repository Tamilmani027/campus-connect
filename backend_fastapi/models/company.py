from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend_fastapi.database import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    sector = Column(String(100), nullable=True)
    logo_file_id = Column(Integer, ForeignKey('file_storage.id'), nullable=True)
    profile_doc_id = Column(Integer, ForeignKey('file_storage.id'), nullable=True)
    
    logo = relationship("FileStorage", foreign_keys=[logo_file_id], uselist=False)
    profile_doc = relationship("FileStorage", foreign_keys=[profile_doc_id], uselist=False)
