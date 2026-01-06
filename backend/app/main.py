import torch
torch.set_num_threads(1) 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection 

# 👇 UNCOMMENTED PREDICT ROUTES
from app.api import auth_routes, ocr_routes, history_routes, timetable_routes, predict_routes

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(ocr_routes.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(history_routes.router, prefix="/api/v1/history", tags=["History"])
app.include_router(timetable_routes.router, prefix="/api/v1/timetable", tags=["Timetable"])

# 👇 THIS MUST BE UNCOMMENTED FOR IT TO WORK
app.include_router(predict_routes.router, prefix="/api/v1/predict", tags=["Prediction"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Should I Bunk API"}