from fastapi import APIRouter, HTTPException, Depends
from app.core.security import get_current_user
from app.db.mongodb import db
from app.core.config import settings
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import joblib

router = APIRouter()

# Load Model
try:
    model = joblib.load("app/ml/model_pipeline.pkl")
    print("✅ Prediction Model Loaded")
except:
    model = None
    print("⚠️ Model NOT found")

class PredictionInput(BaseModel):
    overall_attendance: float
    is_core_subject: int
    days_to_exam: int
    semester_phase: int
    faculty_strictness: int
    is_lab: bool
    filename: str = "screenshot.png"
    
    # --- MASALA INPUTS ---
    has_proxy: bool
    bunked_last_class: bool
    is_first_period: bool

@router.post("/") 
async def predict_bunk(
    input_data: PredictionInput,
    current_user: dict = Depends(get_current_user)
):
    # Base Score (Attendance)
    score = input_data.overall_attendance
    message = ""
    
    # --- 1. THE PROXY CARD (The Ultimate Shield) ---
    if input_data.has_proxy:
        score += 200 # Instant Safe Mode
        message += "Proxy sorted? Then what are you waiting for? Sleep! 🛌 "
        # Skip other logic if proxy is set, because nothing else matters
    
    else:
        # --- 2. THE DANGER ZONE (No Proxy) ---
        
        # Consective Bunk Penalty (Teacher Memory)
        if input_data.bunked_last_class:
            score -= 40
            message += "You skipped last time. Teacher will definitely mark you absent today. "

        # Lab Penalty
        if input_data.is_lab:
            score -= 50
            message += "It's a LAB. Don't be stupid. Go. "
        
        # Strict Faculty
        if input_data.faculty_strictness == 3:
            score -= 20
            message += "Faculty is strict. "
        elif input_data.faculty_strictness == 1:
            score += 15
            message += "Faculty is chill. "

        # First Period Bonus (Empathy Factor)
        if input_data.is_first_period and not input_data.is_lab:
            score += 10
            message += "First hour is tough. If you're really sleepy, maybe risk it. "

        # Exam Panic
        if input_data.days_to_exam < 5:
            score -= 100
            message = "EXAMS ARE HERE. GO STUDY. " + message

    # Attendance Reality Check
    if input_data.overall_attendance < 65 and not input_data.has_proxy:
        score = 0
        message = "Detention Risk. You cannot afford to bunk. "

    # --- FINAL VERDICT ---
    if score >= 80:
        verdict = "Safe to Bunk 😎"
        if not message: message = "Clear skies. Enjoy your freedom."
    elif 50 <= score < 80:
        verdict = "Risky... 🎲"
        if not message: message = "Flip a coin. It's 50/50."
    else:
        verdict = "DO NOT BUNK ☠️"
        if not message: message = "Get to class immediately."

    # Save to DB
    database = db.client[settings.DATABASE_NAME]
    log_entry = {
        "username": current_user["sub"],
        "filename": input_data.filename,
        "overall_attendance": input_data.overall_attendance,
        "prediction": verdict,
        "timestamp": datetime.utcnow()
    }
    await database["history"].insert_one(log_entry)

    return {
        "prediction": verdict,
        "message": message,
        "confidence": "B.Tech Logic Applied"
    }