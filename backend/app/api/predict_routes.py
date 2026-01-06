import os
import json
import google.generativeai as genai
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from app.db.mongodb import db
from app.core.config import settings
from app.core.security import get_current_user

load_dotenv()

router = APIRouter()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- HELPER: AUTO-SELECT MODEL ---
def get_best_available_model():
    try:
        # Just use Flash. It is the most reliable for free tier rate limits.
        return "gemini-1.5-flash"
    except:
        return "gemini-1.5-flash"

CURRENT_MODEL_NAME = get_best_available_model()

class PredictionRequest(BaseModel):
    overall_attendance: float
    is_core_subject: int
    days_to_exam: int
    semester_phase: int
    faculty_strictness: int
    is_lab: bool
    has_proxy: bool
    bunked_last_class: bool
    is_first_period: bool
    filename: str

# --- VINTAGE MATH MODEL (CORRECTED LOGIC) ---
def calculate_vintage_risk(data: PredictionRequest):
    # 1. Sanitize Inputs (No negative days)
    if data.days_to_exam < 0:
        data.days_to_exam = 0

    # 2. Initialize Score ONCE
    score = 0.0

    # 3. Attendance Impact (The Foundation)
    if data.overall_attendance < 75: 
        score += (75 - data.overall_attendance) * 2.5
    elif data.overall_attendance > 85: 
        score -= 10

    # 4. Exam Panic (Cumulative)
    if data.days_to_exam <= 3: 
        score += 60
    elif data.days_to_exam <= 7: 
        score += 30
    
    # 5. Contextual Weights
    if data.is_lab: score += 25
    if data.faculty_strictness == 3: score += 20
    if data.faculty_strictness == 1: score -= 10
    if data.bunked_last_class: score += 15

    # 6. The Saviors
    if data.has_proxy: score -= 45
    if data.is_first_period: score -= 10

    # 7. Final Calculations
    final_risk = max(0, min(100, score))
    is_safe = final_risk < 50
    
    # Generate Message
    reasons = []
    if data.days_to_exam <= 3: reasons.append("Exam imminent")
    if data.overall_attendance < 75: reasons.append("Low attendance")
    if data.is_lab: reasons.append("Lab session")
    if data.has_proxy: reasons.append("Proxy available")
    
    msg_text = ", ".join(reasons) if reasons else "Standard conditions"

    return {
        "prediction": "Safe to Bunk 😎" if is_safe else "Not Safe ❌",
        "confidence": f"{100 - final_risk:.1f}%" if is_safe else f"{final_risk:.1f}% Risk",
        "message": f"Calculated Risk: {int(final_risk)}%. {msg_text}."
    }

@router.post("/", status_code=200)
async def predict_risk(data: PredictionRequest, current_user: dict = Depends(get_current_user)):
    result = {}
    
    # 1. Try Gemini
    try:
        model = genai.GenerativeModel(CURRENT_MODEL_NAME)
        prompt = f"""
        Act as a College Advisor. 
        Attendance: {data.overall_attendance}%, Exam in: {data.days_to_exam} days, Proxy: {data.has_proxy}.
        Return JSON: {{ "prediction": "Safe/Not Safe", "confidence": "85%", "message": "Short reason" }}
        """
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean_text)
    except Exception:
        # Fallback to Vintage Math
        result = calculate_vintage_risk(data)

    # 2. SAVE TO DATABASE
    try:
        username = current_user.get("username") or current_user.get("sub") or "unknown"
        history_log = {
            "username": username,
            "timestamp": datetime.now(),
            "overall_attendance": data.overall_attendance,
            "filename": data.filename,
            "prediction": result.get("prediction", "Unknown"),
            "confidence": result.get("confidence", "0%"),
            "message": result.get("message", "")
        }
        database = db.client[settings.DATABASE_NAME]
        await database["history"].insert_one(history_log)
        
    except Exception as e:
        print(f"❌ DB Save Error: {e}")

    return result