from sqlalchemy import Column, Integer, String, Text, DateTime, func
from ..database import Base

class Resource(Base):
	__tablename__ = "resources"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(150), nullable=False)
	url = Column(String(500), nullable=False)
	description = Column(Text, nullable=True)
	created_at = Column(DateTime, server_default=func.now(), nullable=False)

class ResumeSample(Base):
	__tablename__ = "resume_samples"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(150), nullable=False)
	url = Column(String(500), nullable=False)
	created_at = Column(DateTime, server_default=func.now(), nullable=False)

class Announcement(Base):
	__tablename__ = "announcements"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(150), nullable=False)
	content = Column(Text, nullable=False)
	created_at = Column(DateTime, server_default=func.now(), nullable=False)


