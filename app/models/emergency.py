from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class EmergencyStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EmergencyBase(BaseModel):
    patient_id: str
    hospital_id: Optional[str] = None
    description: Optional[str] = None
    location: dict # GeoJSON point
    status: EmergencyStatus = EmergencyStatus.PENDING

class EmergencyCreate(EmergencyBase):
    pass

class EmergencyInDB(EmergencyBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
