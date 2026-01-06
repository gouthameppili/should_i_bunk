import torch
torch.set_num_threads(1) 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# 👇 CHANGED THIS LINE: Point to 'app.db.mongodb' instead of 'database'
from app.db.mongodb import connect_to_mongo, close_mongo_connection 

from app.api import auth_routes, ocr_routes, history_routes, timetable_routes 
# from app.api import predict_routes  <-- Keep commented out

app = FastAPI(title=settings.PROJECT_NAME)

# --- CORS Setup ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Events ---
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# --- Routes ---
app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(ocr_routes.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(history_routes.router, prefix="/api/v1/history", tags=["History"])
app.include_router(timetable_routes.router, prefix="/api/v1/timetable", tags=["Timetable"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Should I Bunk API"}