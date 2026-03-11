from fastapi import APIRouter, Depends, HTTPException
from app.database.mongodb import get_database
from app.models.emergency import EmergencyCreate, EmergencyInDB, EmergencyStatus
import uuid
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/sos", response_model=EmergencyInDB)
async def create_sos(emergency: EmergencyCreate, db=Depends(get_database)):
    emergency_dict = emergency.dict()
    emergency_dict["_id"] = str(uuid.uuid4())
    emergency_dict["created_at"] = datetime.utcnow()
    
    await db["emergency_requests"].insert_one(emergency_dict)
    return emergency_dict

@router.get("/active", response_model=List[EmergencyInDB])
async def get_active_emergencies(db=Depends(get_database)):
    cursor = db["emergency_requests"].find({"status": EmergencyStatus.PENDING})
    requests = await cursor.to_list(length=100)
    return requests

@router.patch("/{request_id}/status")
async def update_sos_status(request_id: str, status: EmergencyStatus, db=Depends(get_database)):
    result = await db["emergency_requests"].update_one(
        {"_id": request_id},
        {"$set": {"status": status}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"message": "Status updated"}
