from fastapi import APIRouter, Depends, Query, HTTPException
from app.database.mongodb import get_database
from app.models.ambulance import AmbulanceCreate, AmbulanceInDB, AmbulanceStatus
import uuid
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/", response_model=AmbulanceInDB)
async def register_ambulance(ambulance: AmbulanceCreate, db=Depends(get_database)):
    ambulance_dict = ambulance.dict()
    ambulance_dict["_id"] = str(uuid.uuid4())
    ambulance_dict["updated_at"] = datetime.utcnow()
    
    await db["ambulances"].create_index([("location", "2dsphere")])
    await db["ambulances"].insert_one(ambulance_dict)
    return ambulance_dict

@router.get("/nearby", response_model=List[AmbulanceInDB])
async def get_nearby_ambulances(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(10.0),
    db=Depends(get_database)
):
    radius_meters = radius_km * 1000
    query = {
        "status": AmbulanceStatus.AVAILABLE,
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "$maxDistance": radius_meters
            }
        }
    }
    cursor = db["ambulances"].find(query)
    ambulances = await cursor.to_list(length=100)
    return ambulances

@router.patch("/{ambulance_id}/location")
async def update_location(ambulance_id: str, lat: float, lng: float, db=Depends(get_database)):
    await db["ambulances"].update_one(
        {"_id": ambulance_id},
        {"$set": {
            "location": {"type": "Point", "coordinates": [lng, lat]},
            "updated_at": datetime.utcnow()
        }}
    )
    return {"message": "Location updated"}
