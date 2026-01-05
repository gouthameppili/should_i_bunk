import torch
torch.set_num_threads(1)

from fastapi import FastAPI
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.db.mongodb import connect_to_mongo, close_mongo_connection


# Import Routes
from app.api import auth_routes, ocr_routes, predict_routes, history_routes, timetable_routes

app = FastAPI(title=settings.PROJECT_NAME)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB Events
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

# Register Routers
app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(predict_routes.router, prefix="/api/v1/predict", tags=["Prediction"])
app.include_router(timetable_routes.router, prefix="/api/v1/timetable", tags=["Timetable"])
app.include_router(ocr_routes.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(history_routes.router, prefix="/api/v1/history", tags=["History"])

@app.get("/")
async def root():
    return {"message": "Welcome to Should I Bunk? API", "status": "active"}