from pydantic import BaseModel, EmailStr
from typing import Optional

class StudentRegister(BaseModel):
	name: str
	email: EmailStr
	department: Optional[str] = None
	batch: Optional[int] = None
	password: str

class StudentLogin(BaseModel):
	email: EmailStr
	password: str

class StudentOut(BaseModel):
	id: int
	name: str
	email: EmailStr
	department: Optional[str] = None
	batch: Optional[int] = None
	current_streak: int = 0
	class Config:
		from_attributes = True


