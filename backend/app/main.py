import torch
torch.set_num_threads(1) # Keep this!

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# 1. REMOVE or COMMENT OUT 'predict_routes' here:
from app.api import auth_routes, ocr_routes, history_routes, timetable_routes 
# from app.api import predict_routes  <-- COMMENTED OUT

app = FastAPI(title=settings.PROJECT_NAME)

# ... CORS Middleware Setup (Keep this unchanged) ...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Include Routers (Keep others, comment out predict)
app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(ocr_routes.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(history_routes.router, prefix="/api/v1/history", tags=["History"])
app.include_router(timetable_routes.router, prefix="/api/v1/timetable", tags=["Timetable"])

# app.include_router(predict_routes.router, prefix="/api/v1/predict", tags=["Prediction"]) <-- COMMENTED OUT

@app.get("/")
def read_root():
    return {"message": "Welcome to Should I Bunk API"}