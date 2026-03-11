import asyncio
import uuid
from datetime import datetime
from app.database.mongodb import connect_to_mongo, close_mongo_connection, get_database
from app.core.security import get_password_hash

async def seed_data():
    await connect_to_mongo()
    db = get_database()

    # Clear existing data (optional, be careful)
    # await db["users"].delete_many({})
    # await db["hospitals"].delete_many({})

    print("Seeding Users...")
    admin_id = str(uuid.uuid4())
    await db["users"].update_one(
        {"email": "admin@medlink.com"},
        {"$set": {
            "_id": admin_id,
            "name": "System Admin",
            "email": "admin@medlink.com",
            "password": get_password_hash("admin123"),
            "role": "ADMIN",
            "created_at": datetime.utcnow()
        }},
        upsert=True
    )

    print("Seeding Hospitals...")
    hospitals = [
        {
            "_id": str(uuid.uuid4()),
            "name": "City General Hospital",
            "address": "123 Healthcare Ave, Metro City",
            "location": {"type": "Point", "coordinates": [77.2090, 28.6139]},
            "icu_beds": 15,
            "ventilators": 8,
            "oxygen_cylinders": 50,
            "phone": "+91 9876543210",
            "admin_id": admin_id,
            "updated_at": datetime.utcnow()
        },
        {
            "_id": str(uuid.uuid4()),
            "name": "Emergency Care Center",
            "address": "456 Safety Road, North Delhi",
            "location": {"type": "Point", "coordinates": [77.2210, 28.6340]},
            "icu_beds": 5,
            "ventilators": 2,
            "oxygen_cylinders": 20,
            "phone": "+91 9123456789",
            "admin_id": admin_id,
            "updated_at": datetime.utcnow()
        }
    ]
    
    for h in hospitals:
        await db["hospitals"].update_one({"name": h["name"]}, {"$set": h}, upsert=True)
    
    # Ensure index
    await db["hospitals"].create_index([("location", "2dsphere")])

    print("Finished seeding data!")
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(seed_data())
