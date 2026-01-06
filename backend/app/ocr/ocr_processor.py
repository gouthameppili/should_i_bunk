import google.generativeai as genai
import os
import re
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
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 🟢 STRATEGY: Simple text dump. Don't ask for JSON.
        prompt = "Read all the text in this image. Return it as plain text."
        
        time.sleep(1)
        response = model.generate_content([prompt, image])
        text = response.text
        
        # Log what Gemini actually sees (Check your Render logs for this!)
        print(f"🔍 RAW OCR OUTPUT:\n{text}")

        # 🟢 LOGIC 1: Look for the specific "TOTAL" row pattern
        # Matches "TOTAL", then some numbers, then ends with a decimal number
        # Example: "TOTAL 102 94 92.16"
        total_lines = [line for line in text.split('\n') if "TOTAL" in line.upper()]
        
        for line in total_lines:
            # Remove symbols like '|' or '%'
            clean_line = line.replace('|', '').replace('%', '').strip()
            # Find all numbers in that line (e.g. ['102', '94', '92.16'])
            numbers = re.findall(r"[\d\.]+", clean_line)
            
            if numbers:
                # The percentage is usually the LAST number
                try:
                    percent = float(numbers[-1])
                    # Sanity check: Attendance is usually between 0 and 100
                    if 0 <= percent <= 100:
                        return {"overall_attendance": percent, "subjects": [], "raw_text": text}
                except:
                    continue

        # 🟢 LOGIC 2: Fallback - Look for "Overall" or "%" explicitly
        # Matches "92.16 %" or "92.16%"
        percent_match = re.search(r"(\d+\.?\d*)\s*%", text)
        if percent_match:
             return {"overall_attendance": float(percent_match.group(1)), "subjects": [], "raw_text": text}

        # If we failed, return raw text so we can see it in the UI
        result_data["raw_text"] = text
        return result_data

    except Exception as e:
        print(f"🔥 OCR Logic Error: {str(e)}")
        if "429" in str(e):
             return {"overall_attendance": 0.0, "error": "Rate Limit. Wait 1 min."}
        return result_data