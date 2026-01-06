import google.generativeai as genai
import os
import json
from io import BytesIO
from PIL import Image

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def extract_attendance_from_image(file_bytes: bytes):
    result_data = {"overall_attendance": 0.0, "subjects": [], "raw_text": ""}

    try:
        image = Image.open(BytesIO(file_bytes))
        
        # Use standard flash model (lowest latency, highest stability)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = """
        Read the attendance percentage from this image.
        Look for "Overall", "Total", or the main percentage circle.
        Return JSON ONLY: {"overall_attendance": 85.5, "subjects": []}
        If you cannot read it, return {"overall_attendance": 0.0, "subjects": []}
        """

        response = model.generate_content([prompt, image])
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_text)

    except Exception as e:
        print(f"🔥 OCR Error: {str(e)}")
        # If Rate Limit (429) happens, we return this specific error
        if "429" in str(e):
            return {"overall_attendance": 0.0, "subjects": [], "raw_text": "Rate Limit: Please wait 1 minute."}
        return result_data