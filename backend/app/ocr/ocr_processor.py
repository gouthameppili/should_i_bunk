import google.generativeai as genai
import os
import re  # 👈 Added Regex for manual extraction
import json
import time
from io import BytesIO
from PIL import Image

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def extract_attendance_from_image(file_bytes: bytes):
    result_data = {"overall_attendance": 0.0, "subjects": [], "raw_text": ""}

    try:
        image = Image.open(BytesIO(file_bytes))
        
        # Use Standard Flash (Reliable)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 🟢 STRATEGY CHANGE: Ask for raw text of the bottom row, not JSON
        prompt = """
        Look at the bottom of this table.
        Find the row that starts with "TOTAL".
        Write down the exact text of that entire row.
        Then, identify the final percentage number in that row.
        
        Return the result in this exact format:
        Row: [text of the row]
        Percentage: [number]
        """
        
        time.sleep(1) # Safety buffer
        response = model.generate_content([prompt, image])
        text = response.text
        
        print(f"🔍 Gemini Raw Output: {text}") # Check logs to see what it sees!

        # 🟢 MANUAL EXTRACTION (Regex)
        # We look for a number (like 92.16 or 85.00) specifically near "Percentage:" or at end of string
        match = re.search(r"Percentage:\s*([\d\.]+)", text)
        if match:
            percent = float(match.group(1))
            return {"overall_attendance": percent, "subjects": [], "raw_text": text}
        
        # Fallback: Search for any number after "TOTAL"
        # Matches "TOTAL 102 94 92.16" -> grabs 92.16
        fallback_match = re.search(r"TOTAL.*?([\d\.]+)\s*$", text.replace("\n", " ").strip())
        if fallback_match:
             percent = float(fallback_match.group(1))
             return {"overall_attendance": percent, "subjects": [], "raw_text": text}

        return result_data

    except Exception as e:
        print(f"🔥 OCR Logic Error: {str(e)}")
        if "429" in str(e):
             return {"overall_attendance": 0.0, "error": "Rate Limit. Wait 1 min."}
        return result_data