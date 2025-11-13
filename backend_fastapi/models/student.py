from sqlalchemy import Column, Integer, String, DateTime, func
from backend_fastapi.database import Base

class Student(Base):
	__tablename__ = "students"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String(100), nullable=False)
	email = Column(String(120), unique=True, index=True, nullable=False)
	department = Column(String(50), nullable=True)
	batch = Column(Integer, nullable=True)
	password_hash = Column(String(255), nullable=False)
	created_at = Column(DateTime, server_default=func.now(), nullable=False)


