from pydantic import BaseModel, AnyUrl
from typing import Optional
from datetime import datetime
from file_storage import FileStorageOut

class ResourceCreate(BaseModel):
    title: str
    url: Optional[AnyUrl] = None
    description: Optional[str] = None

class ResourceOut(BaseModel):
    id: int
    title: str
    url: Optional[str] = None
    description: Optional[str] = None
    file: Optional[FileStorageOut] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeCreate(BaseModel):
    title: str
    url: Optional[AnyUrl] = None

class ResumeOut(BaseModel):
    id: int
    title: str
    url: Optional[str] = None
    file: Optional[FileStorageOut] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AnnouncementCreate(BaseModel):
    title: str
    content: str

class AnnouncementOut(BaseModel):
    id: int
    title: str
    content: str
    file: Optional[FileStorageOut] = None
    created_at: datetime

    class Config:
        from_attributes = True


