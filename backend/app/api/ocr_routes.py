from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.ocr.ocr_processor import extract_attendance_from_image
from app.core.security import get_current_user

# Note: We REMOVED joblib and pandas to save RAM on Render Free Tier.
# This endpoint now ONLY does text extraction.

router = APIRouter()

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

    # 3. Run OCR (Now using Gemini via ocr_processor)
    try:
        # returns a dictionary: {"overall_attendance": 85.0, "subjects": [...], "raw_text": "..."}
        data = extract_attendance_from_image(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Engine Error: {str(e)}")

    # 4. Check if we found anything (Gemini usually returns valid JSON structure even on failure)
    if "error" in data:
         raise HTTPException(status_code=500, detail=data["error"])

    # 5. Return Clean Data
    # We removed the "ai_analysis" (Prediction) part because it requires heavy libraries.
    # The Frontend will use this data to fill the form, then the User clicks "Predict".
    return {
        "extracted_data": {
            "overall_attendance": data.get("overall_attendance", 0.0),
            "subject_attendances": data.get("subjects", [])
        },
        "raw_text": data.get("raw_text", "")
    }