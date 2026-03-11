from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DonorBase(BaseModel):
    user_id: str
    blood_group: str
    location: dict # GeoJSON point: {"type": "Point", "coordinates": [lng, lat]}
    is_available: bool = True
    last_donation: Optional[datetime] = None

class DonorCreate(DonorBase):
    pass

class DonorInDB(DonorBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
