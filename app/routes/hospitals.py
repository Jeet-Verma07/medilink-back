from fastapi import APIRouter, Depends, HTTPException, Query
from app.database.mongodb import get_database
from app.models.hospital import HospitalCreate, HospitalInDB, ResourceUpdate
from typing import List
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=HospitalInDB)
async def create_hospital(hospital: HospitalCreate, db=Depends(get_database)):
    hospital_dict = hospital.dict()
    hospital_dict["_id"] = str(uuid.uuid4())
    hospital_dict["updated_at"] = datetime.utcnow()
    
    # Ensure geospatial index exists
    await db["hospitals"].create_index([("location", "2dsphere")])
    
    await db["hospitals"].insert_one(hospital_dict)
    return hospital_dict

@router.get("/nearby", response_model=List[HospitalInDB])
async def get_nearby_hospitals(
    lat: float = Query(...), 
    lng: float = Query(...), 
    radius_km: float = Query(10.0),
    db=Depends(get_database)
):
    # Radius in meters
    radius_meters = radius_km * 1000
    
    query = {
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
    
    cursor = db["hospitals"].find(query)
    hospitals = await cursor.to_list(length=100)
    return hospitals

@router.patch("/{hospital_id}/resources", response_model=HospitalInDB)
async def update_resources(hospital_id: str, resources: ResourceUpdate, db=Depends(get_database)):
    update_data = resources.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db["hospitals"].find_one_and_update(
        {"_id": hospital_id},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return result
