from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    PATIENT = "PATIENT"
    HOSPITAL = "HOSPITAL"
    DONOR = "DONOR"
    AMBULANCE = "AMBULANCE"
    ADMIN = "ADMIN"

class Location(BaseModel):
    lat: float
    lng: float

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    role: UserRole
    location: Optional[Location] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[Location] = None

class UserInDB(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
