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

# --- COPY THE HELPER FUNCTION HERE TOO ---
def get_best_available_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority: Flash > Pro > Any
        priorities = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
        
        for p in priorities:
            for m in available_models:
                if p in m: return m
        
        return available_models[0] if available_models else "gemini-1.5-flash"
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

# ... (Keep calculate_vintage_risk function exactly as it was) ...
def calculate_vintage_risk(data: PredictionRequest):
    # (Paste your vintage logic here from previous step)
    # Short version for brevity:
    score = 0.0
    if data.overall_attendance < 75: score += (75 - data.overall_attendance) * 2.5
    if data.days_to_exam <= 3: score += 60
    if data.has_proxy: score -= 45
    final_risk = max(0, min(100, score))
    is_safe = final_risk < 50
    return {
        "prediction": "Safe to Bunk 😎" if is_safe else "Not Safe ❌",
        "confidence": f"{100 - final_risk:.1f}%",
        "message": "Calculated Risk."
    }

@router.post("/", status_code=200)
async def predict_risk(data: PredictionRequest, current_user: dict = Depends(get_current_user)):
    result = {}
    
    # 1. Try Gemini (Auto-Selected)
    try:
        model = genai.GenerativeModel(CURRENT_MODEL_NAME)
        prompt = f"""
        Act as a College Advisor. 
        Attendance: {data.overall_attendance}%, Exam in: {data.days_to_exam} days, Proxy: {data.has_proxy}.
        Return JSON: {{ "prediction": "Safe/Not Safe", "confidence": "85%", "message": "Short reason" }}
        """
        response = model.generate_content(prompt)
        result = json.loads(response.text.replace("```json", "").replace("```", "").strip())
    except Exception:
        # Fallback to Vintage Math
        result = calculate_vintage_risk(data)

    # 2. SAVE TO DATABASE (Keep this part!)
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