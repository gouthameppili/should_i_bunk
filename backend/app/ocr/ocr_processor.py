import google.generativeai as genai
import os
import json
from io import BytesIO
from PIL import Image

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def extract_attendance_from_image(file_bytes: bytes):
    # Default return if everything fails
    result_data = {"overall_attendance": 0.0, "subjects": [], "raw_text": ""}

    try:
        image = Image.open(BytesIO(file_bytes))
        
        # 🟢 FIX 1: Use 'gemini-1.5-flash-latest' (Safer Alias)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # 🟢 FIX 2: Better Prompt for your specific table format
        prompt = """
        Analyze this "Attendance Report".
        1. Find the row "TOTAL" at the bottom.
        2. Extract the percentage in the last column (e.g., 92.16).
        3. Return JSON ONLY: {"overall_attendance": 92.16}
        If you can't find it, return {"overall_attendance": 0.0}
        """

        response = model.generate_content([prompt, image])
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        
        parsed = json.loads(clean_text)
        result_data.update(parsed)
        return result_data

    except Exception as e:
        print(f"🔥 OCR Error: {str(e)}")
        # Fallback: If AI fails, return 0 so the user can manually enter it if needed
        return result_data