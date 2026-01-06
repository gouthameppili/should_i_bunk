import google.generativeai as genai
import os
from io import BytesIO
from PIL import Image
from app.core.config import settings

# Configure the API
# We will grab the key from settings/env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_attendance_from_image(file_bytes: bytes):
    try:
        # 1. Load image from bytes
        image = Image.open(BytesIO(file_bytes))

        # 2. Initialize Gemini Model (Lightweight 1.5 Flash)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 3. The Prompt - We ask Gemini to do the hard work
        prompt = """
        Analyze this image of an attendance record. 
        Extract the following:
        1. The Overall Attendance percentage (look for "Total", "Overall", or the main percentage).
        2. A list of subject attendance percentages.
        
        Return ONLY a JSON string like this:
        {"overall_attendance": 85.5, "subjects": [80.0, 90.0, 75.5], "raw_text": "Summary of text..."}
        """

        # 4. Generate Content
        response = model.generate_content([prompt, image])
        
        # 5. Parse the result (Simple cleaning)
        # Gemini sometimes puts ```json ... ``` blocks, we clean them
        text_response = response.text.replace("```json", "").replace("```", "").strip()
        
        import json
        data = json.loads(text_response)
        
        return data

    except Exception as e:
        print(f"Gemini Error: {e}")
        # Fallback if AI fails
        return {
            "raw_text": "Error processing image",
            "overall_attendance": 0.0,
            "subjects": []
        }