from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from backend_fastapi.database import Base

class FileStorage(Base):
    __tablename__ = "file_storage"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)  # e.g., 'company', 'resource', 'resume', 'announcement'
    entity_id = Column(Integer, nullable=True)  # ID of the related entity
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)