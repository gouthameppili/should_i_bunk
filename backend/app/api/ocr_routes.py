from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.ocr.ocr_processor import extract_attendance_from_image
from app.core.security import get_current_user
import joblib
import pandas as pd

router = APIRouter()

try:
    model = joblib.load("app/ml/model_pipeline.pkl")
    print("✅ Model loaded in OCR module")
except:
    model = None

@router.post("/scan", tags=["OCR"])
async def scan_attendance(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # 1. Validate Image
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload JPEG or PNG.")

    # 2. Read Image Bytes
    image_bytes = await file.read()

    # 3. Run OCR
    try:
        overall, subjects = extract_attendance_from_image(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Engine Error: {str(e)}")

    if overall == 0.0:
        return {"message": "Could not read any attendance numbers. Try a clearer image."}

    # 4. Prepare Data for Initial "Quick Prediction"
    # The OCR doesn't know if it's a Core subject or Exam day, 
    # so we assume a "Neutral/Safe" default for the preview.
    
    input_features = pd.DataFrame([{
        'overall_attendance': overall,
        'is_core_subject': 1,   # Assume it's important (Safe default)
        'days_to_exam': 30,     # Assume no exam immediately
        'semester_phase': 1     # Assume mid-semester
    }])

    # 5. Predict Risk
    prediction = 0
    confidence = 0.0
    
    if model:
        try:
            prediction = model.predict(input_features)[0]
            confidence = model.predict_proba(input_features)[0][1]
        except Exception as e:
            print(f"⚠️ Prediction Error: {e}")
            # Fallback if model expects different columns
            prediction = 0 

    result_text = "Safe to Bunk 😎" if prediction == 1 else "Not Safe ❌"

    return {
        "extracted_data": {
            "overall_attendance": overall,
            "subject_attendances": subjects
        },
        "ai_analysis": {
            "prediction": result_text,
            "confidence": f"{confidence:.2f}",
            "note": "Initial scan. Please answer the popup questions for accuracy."
        }
    }