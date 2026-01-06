import os
import json
import google.generativeai as genai
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# Setup Gemini (Uses the same key you already added)
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

@router.post("/risk", status_code=200)
async def predict_risk(data: PredictionRequest):
    # 1. Construct the prompt with all the variables
    prompt = f"""
    Act as a strict College Attendance Risk Analyzer AI. 
    Analyze the following student situation and calculate the risk of bunking this class.
    
    Student Stats:
    - Overall Attendance: {data.overall_attendance}%
    - Subject Type: {"Core Subject (Important)" if data.is_core_subject else "Elective/Common"}
    - Days to Exam: {data.days_to_exam}
    - Semester Phase: {["Start", "Mid", "End"][data.semester_phase]}
    - Faculty Strictness (1-3): {data.faculty_strictness}
    - Is Lab Session: {data.is_lab}
    - Has Proxy (Friend inside): {data.has_proxy}
    - Bunked Last Class: {data.bunked_last_class}
    - First Period: {data.is_first_period}

    Task:
    1. Calculate a "Risk Score" (0 to 100).
    2. Determine a verdict: "Safe to Bunk 😎" or "Not Safe ❌".
    3. Write a short, witty, context-aware reason.

    Return ONLY JSON in this format:
    {{
        "prediction": "Safe to Bunk 😎" or "Not Safe ❌",
        "confidence": "85%",
        "message": "Reasoning here..."
    }}
    """

    try:
        # 2. Ask Gemini 2.0 Flash (Fast & Smart)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        # 3. Clean and Parse Response
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean_text)
        
        return result

    except Exception as e:
        print(f"AI Prediction Error: {e}")
        # Fallback to manual logic ONLY if AI fails (Safety Net)
        return {
            "prediction": "Not Safe ❌",
            "confidence": "50% (Fallback)",
            "message": "AI Brain is unreachable, but with your attendance, better safe than sorry!"
        }