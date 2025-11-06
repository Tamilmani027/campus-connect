from pydantic import BaseModel, AnyUrl
from typing import Optional

class ResourceCreate(BaseModel):
	title: str
	url: AnyUrl
	description: Optional[str] = None

class ResourceOut(ResourceCreate):
	id: int
	class Config:
		from_attributes = True

class ResumeCreate(BaseModel):
	title: str
	url: AnyUrl

class ResumeOut(ResumeCreate):
	id: int
	class Config:
		from_attributes = True

class AnnouncementCreate(BaseModel):
	title: str
	content: str

class AnnouncementOut(AnnouncementCreate):
	id: int
	class Config:
		from_attributes = True


