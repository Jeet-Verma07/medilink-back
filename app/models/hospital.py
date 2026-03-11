from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ResourceUpdate(BaseModel):
    icu_beds: int
    ventilators: int
    oxygen_cylinders: int

class HospitalBase(BaseModel):
    name: str
    address: str
    location: dict # GeoJSON point: {"type": "Point", "coordinates": [lng, lat]}
    icu_beds: int
    ventilators: int
    oxygen_cylinders: int
    phone: str
    admin_id: str

class HospitalCreate(HospitalBase):
    pass

class HospitalInDB(HospitalBase):
    id: str = Field(alias="_id")
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
