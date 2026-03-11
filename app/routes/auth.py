from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.database.mongodb import get_database
from app.models.user import UserCreate, UserInDB, UserRole
from app.core.security import get_password_hash, verify_password, create_access_token
from app.utils.email import send_otp_email
from datetime import datetime, timedelta
import uuid
import random

router = APIRouter()

@router.post("/request-otp")
async def request_otp(email: str, db=Depends(get_database)):
    # Generate 6-digit OTP
    otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
    expiry = datetime.utcnow() + timedelta(minutes=10)
    
    # Store OTP in DB (transient)
    await db["otps"].update_one(
        {"email": email},
        {"$set": {"otp": otp, "expiry": expiry}},
        upsert=True
    )
    
    # Send email
    success = await send_otp_email(email, otp)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP email")
    
    return {"message": "OTP sent successfully"}

@router.post("/verify-otp")
async def verify_otp(email: str, otp: str, db=Depends(get_database)):
    stored_otp = await db["otps"].find_one({"email": email})
    
    if not stored_otp or stored_otp["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if datetime.utcnow() > stored_otp["expiry"]:
        raise HTTPException(status_code=400, detail="OTP expired")
    
    # Delete OTP after verification
    await db["otps"].delete_one({"email": email})
    
    # Check if user exists
    user = await db["users"].find_one({"email": email})
    if not user:
        # Auto-create user as PATIENT if not exists
        user_id = str(uuid.uuid4())
        user = {
            "_id": user_id,
            "email": email,
            "name": email.split("@")[0],
            "role": "PATIENT",
            "created_at": datetime.utcnow(),
            "phone": ""
        }
        await db["users"].insert_one(user)
    
    access_token = create_access_token(subject=user["_id"])
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}

@router.post("/register", response_model=UserInDB)
async def register(user_in: UserCreate, db=Depends(get_database)):
    user_exists = await db["users"].find_one({"email": user_in.email})
    if user_exists:
        raise HTTPException(status_code=400, detail="User already registered")
    
    user_dict = user_in.dict()
    user_dict["_id"] = str(uuid.uuid4())
    user_dict["password"] = get_password_hash(user_dict["password"])
    user_dict["created_at"] = datetime.utcnow()
    
    await db["users"].insert_one(user_dict)
    return user_dict

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_database)):
    user = await db["users"].find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token = create_access_token(subject=user["_id"])
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}
