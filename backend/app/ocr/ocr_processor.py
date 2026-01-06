import google.generativeai as genai
import os
import re
from io import BytesIO
from PIL import Image

# Setup API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def extract_attendance_from_image(file_bytes: bytes):
    result_data = {"overall_attendance": 0.0, "subjects": [], "raw_text": ""}

    try:
        image = Image.open(BytesIO(file_bytes))
        
        # Use Standard Flash (Reliable on Free Tier)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 1. Ask for a simple text dump
        prompt = "Read all the text in this image. Return it as plain text. Do not format it."
        
        response = model.generate_content([prompt, image])
        text = response.text
        
        # 🟢 DEBUGGING: This will print EXACTLY what Gemini sees to your Render logs
        print(f"\n🔍 GEMINI SAW THIS:\n{text}\n")
        
        # 🟢 STRATEGY: The "Decimal Hunter"
        # 1. Find where "TOTAL" starts
        total_index = text.upper().find("TOTAL")
        
        if total_index != -1:
            # 2. Slice the text to only look ATFER "TOTAL"
            text_after_total = text[total_index:]
            
            # 3. Find all decimal numbers (e.g., 92.16, 85.5) in that chunk
            # The regex matches numbers that HAVE a dot
            decimal_matches = re.findall(r"\b\d+\.\d+\b", text_after_total)
            
            if decimal_matches:
                # The first decimal after "TOTAL" is usually the percentage
                percent = float(decimal_matches[0])
                
                # Sanity check: Percentage must be 0-100
                if 0 <= percent <= 100:
                    print(f"✅ FOUND PERCENTAGE: {percent}")
                    return {"overall_attendance": percent, "subjects": [], "raw_text": text}

        # 🔴 FALLBACK: If "TOTAL" is missing, just hunt for the highest decimal number in the whole text
        # (This helps if Gemini misses the word "TOTAL")
        all_decimals = re.findall(r"\b\d+\.\d+\b", text)
        valid_percentages = [float(x) for x in all_decimals if 50 <= float(x) <= 100]
        
        if valid_percentages:
            # Take the largest value (assuming attendance is the main metric)
            best_guess = max(valid_percentages)
            print(f"⚠️ GUESSED PERCENTAGE: {best_guess}")
            return {"overall_attendance": best_guess, "subjects": [], "raw_text": text}

        print("❌ NO PERCENTAGE FOUND")
        return result_data

    except Exception as e:
        print(f"🔥 OCR Error: {str(e)}")
        # If rate limited, tell the frontend
        if "429" in str(e):
             return {"overall_attendance": 0.0, "error": "Server Busy (Rate Limit)"}
        return result_data