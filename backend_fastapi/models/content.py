from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Resource(Base):
	__tablename__ = "resources"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(150), nullable=False)
	url = Column(String(500), nullable=True)  # Made nullable since we can have file uploads
	description = Column(Text, nullable=True)
	created_at = Column(DateTime, server_default=func.now(), nullable=False)
	file_id = Column(Integer, ForeignKey('file_storage.id'), nullable=True)
	
	file = relationship("FileStorage", uselist=False)

class ResumeSample(Base):
	__tablename__ = "resume_samples"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(150), nullable=False)
	url = Column(String(500), nullable=True)  # Made nullable since we can have file uploads
	created_at = Column(DateTime, server_default=func.now(), nullable=False)
	file_id = Column(Integer, ForeignKey('file_storage.id'), nullable=True)
	
	file = relationship("FileStorage", uselist=False)

class Announcement(Base):
	__tablename__ = "announcements"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(150), nullable=False)
	content = Column(Text, nullable=False)
	created_at = Column(DateTime, server_default=func.now(), nullable=False)
	file_id = Column(Integer, ForeignKey('file_storage.id'), nullable=True)
	
	file = relationship("FileStorage", uselist=False)


