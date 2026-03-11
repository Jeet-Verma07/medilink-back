from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class AmbulanceStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"

class AmbulanceBase(BaseModel):
    driver_id: str
    vehicle_number: str
    location: dict # GeoJSON point
    status: AmbulanceStatus = AmbulanceStatus.AVAILABLE

class AmbulanceCreate(AmbulanceBase):
    pass

class AmbulanceInDB(AmbulanceBase):
    id: str = Field(alias="_id")
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
