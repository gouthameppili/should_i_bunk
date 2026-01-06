import os
import json
import google.generativeai as genai
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Setup Gemini
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

# --- THE VINTAGE BRAIN REPLICA (Pure Math Model) ---
def calculate_vintage_risk(data: PredictionRequest):
    # Start with a base risk score
    score = 0.0

    # 1. Attendance Impact (Non-linear fear factor)
    # If attendance is > 80, low risk. If < 75, HUGE risk.
    if data.overall_attendance < 75:
        score += (75 - data.overall_attendance) * 2.5  # Heavy penalty
    elif data.overall_attendance > 85:
        score -= 10  # Bonus buffer

    # 2. Exam Panic (Exponential risk)
    if data.days_to_exam <= 3:
        score += 60  # Almost impossible to bunk safely
    elif data.days_to_exam <= 7:
        score += 30
    elif data.days_to_exam > 30:
        score -= 15  # Chill zone

    # 3. Subject & Faculty Weights
    if data.is_core_subject: score += 15
    if data.faculty_strictness == 3: score += 20  # Strict prof
    if data.faculty_strictness == 1: score -= 10  # Chill prof
    
    # 4. Critical Modifiers
    if data.is_lab: score += 25  # Labs are dangerous
    if data.bunked_last_class: score += 15  # Heat check
    
    # 5. The "Saviors"
    if data.has_proxy: score -= 45  # Massive reduction
    if data.is_first_period: score -= 10  # Sleepy prof factor

    # Normalize Score (0 to 100)
    final_risk = max(0, min(100, score))
    
    # Determine Verdict
    # We create a "Confidence" that feels real (e.g. 87% Risk)
    is_safe = final_risk < 50
    
    # Dynamic "Human-like" Reasoning
    reasons = []
    if data.days_to_exam < 5: reasons.append("Exams are too close")
    if data.overall_attendance < 75: reasons.append("Low attendance warning")
    if data.is_lab: reasons.append("Lab session risk")
    if data.has_proxy: reasons.append("Proxy is saving you")
    
    message = f"Risk Level: {int(final_risk)}%. " + (", ".join(reasons) if reasons else "Conditions are standard.")

    return {
        "prediction": "Safe to Bunk 😎" if is_safe else "Not Safe ❌",
        "confidence": f"{100 - final_risk:.1f}%" if is_safe else f"{final_risk:.1f}% Risk",
        "message": message
    }

@router.post("/", status_code=200)
async def predict_risk(data: PredictionRequest):
    # PRIORITY 1: Try Gemini (The Real AI)
    try:
        # Use the most stable model name
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        prompt = f"""
        Act as a strict College Advisor. Analyze this student:
        Attendance: {data.overall_attendance}%, Exam in: {data.days_to_exam} days, 
        Strictness: {data.faculty_strictness}/3, Lab: {data.is_lab}, Proxy: {data.has_proxy}.
        
        Return JSON ONLY:
        {{ "prediction": "Safe to Bunk 😎" or "Not Safe ❌", "confidence": "85%", "message": "Short witty reason." }}
        """
        
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)

    except Exception as e:
        print(f"⚠️ Gemini Unreachable: {e}. Switching to Vintage Math Model.")
        # PRIORITY 2: Fallback to the Vintage Replica (Never fails)
        return calculate_vintage_risk(data)