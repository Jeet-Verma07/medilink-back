from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, hospitals, donors, ambulance, emergency
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.utils.middleware import error_handler_middleware, logging_middleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(title="MedLink API", version="1.0.0", lifespan=lifespan)

# Middleware
app.middleware("http")(error_handler_middleware)
app.middleware("http")(logging_middleware)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to MedLink API"}

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(hospitals.router, prefix="/hospitals", tags=["Hospitals"])
app.include_router(donors.router, prefix="/donors", tags=["Donors"])
app.include_router(ambulance.router, prefix="/ambulance", tags=["Ambulance"])
app.include_router(emergency.router, prefix="/emergency", tags=["Emergency"])
