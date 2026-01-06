import os
import json
import google.generativeai as genai
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from app.db.mongodb import db  # 👈 Added DB import
from app.core.config import settings
from app.core.security import get_current_user # 👈 Added Auth to identify who to save history for

load_dotenv()

router = APIRouter()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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

# --- VINTAGE MATH MODEL (Reliable Fallback) ---
def calculate_vintage_risk(data: PredictionRequest):
    score = 0.0
    if data.overall_attendance < 75: score += (75 - data.overall_attendance) * 2.5
    elif data.overall_attendance > 85: score -= 10
    
    if data.days_to_exam <= 3: score += 60
    elif data.days_to_exam <= 7: score += 30
    elif data.days_to_exam > 30: score -= 15

    if data.is_core_subject: score += 15
    if data.faculty_strictness == 3: score += 20
    if data.faculty_strictness == 1: score -= 10
    
    if data.is_lab: score += 25
    if data.bunked_last_class: score += 15
    if data.has_proxy: score -= 45
    if data.is_first_period: score -= 10

    final_risk = max(0, min(100, score))
    is_safe = final_risk < 50
    
    reasons = []
    if data.days_to_exam < 5: reasons.append("Exams are too close")
    if data.overall_attendance < 75: reasons.append("Low attendance")
    if data.is_lab: reasons.append("Lab session")
    if data.has_proxy: reasons.append("Proxy saved you")
    
    return {
        "prediction": "Safe to Bunk 😎" if is_safe else "Not Safe ❌",
        "confidence": f"{100 - final_risk:.1f}%" if is_safe else f"{final_risk:.1f}% Risk",
        "message": f"Risk Level: {int(final_risk)}%. " + (", ".join(reasons) if reasons else "Conditions are standard.")
    }

@router.post("/", status_code=200)
async def predict_risk(
    data: PredictionRequest,
    current_user: dict = Depends(get_current_user) # 👈 Require User Login to save history
):
    result = {}
    
    # 1. Try Gemini
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Act as a College Advisor. Analyze:
        Attendance: {data.overall_attendance}%, Exam in: {data.days_to_exam} days, 
        Strictness: {data.faculty_strictness}/3, Lab: {data.is_lab}, Proxy: {data.has_proxy}.
        
        Return JSON ONLY:
        {{ "prediction": "Safe to Bunk 😎" or "Not Safe ❌", "confidence": "85%", "message": "Short witty reason." }}
        """
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean_text)
    except Exception as e:
        print(f"⚠️ AI Switch: {e}")
        result = calculate_vintage_risk(data)

    # 2. SAVE TO DATABASE (The Missing Link!) 💾
    try:
        history_log = {
            "username": current_user["username"],
            "timestamp": datetime.now(),
            "overall_attendance": data.overall_attendance,
            "filename": data.filename,
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "message": result["message"]
        }
        database = db.client[settings.DATABASE_NAME]
        await database["history"].insert_one(history_log)
        print("✅ History saved to DB")
    except Exception as e:
        print(f"❌ Failed to save history: {e}")

    return result