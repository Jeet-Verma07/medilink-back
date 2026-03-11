from fastapi import APIRouter, Depends, HTTPException, Query
from app.database.mongodb import get_database
from app.models.donor import DonorCreate, DonorInDB
from typing import List
import uuid

router = APIRouter()

@router.post("/", response_model=DonorInDB)
async def register_donor(donor: DonorCreate, db=Depends(get_database)):
    donor_dict = donor.dict()
    donor_dict["_id"] = str(uuid.uuid4())
    
    # Ensure geospatial index
    await db["blood_donors"].create_index([("location", "2dsphere")])
    
    await db["blood_donors"].insert_one(donor_dict)
    return donor_dict

@router.get("/search", response_model=List[DonorInDB])
async def search_donors(
    blood_group: str = Query(...),
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(20.0),
    db=Depends(get_database)
):
    radius_meters = radius_km * 1000
    
    query = {
        "blood_group": blood_group,
        "is_available": True,
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
    
    cursor = db["blood_donors"].find(query)
    donors = await cursor.to_list(length=100)
    return donors
