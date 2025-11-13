from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileStorageBase(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    file_type: str
    file_size: int
    mime_type: str
    entity_type: str
    entity_id: Optional[int] = None

class FileStorageCreate(FileStorageBase):
    pass

class FileStorageOut(FileStorageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True