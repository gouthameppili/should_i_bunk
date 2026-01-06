import google.generativeai as genai
import os
import json
from io import BytesIO
from PIL import Image

# 1. Setup API Key with explicit check
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ CRITICAL: GEMINI_API_KEY is missing in environment variables!")
else:
    print(f"✅ Gemini API Key found (starts with {api_key[:4]}...)")
    genai.configure(api_key=api_key)

def extract_attendance_from_image(file_bytes: bytes):
    # Default fallback data structure (Matches your probable Pydantic schema)
    result_data = {
        "overall_attendance": 0.0,
        "subjects": [],
        "raw_text": ""
    }

    try:
        # 2. Load Image
        image = Image.open(BytesIO(file_bytes))
        
        # 3. Initialize Model (CORRECT NAME is 'gemini-1.5-flash')
        model = genai.GenerativeModel('gemini-1.5-flash')

        # 4. Prompt
        prompt = """
        Analyze this image. Extract attendance data.
        Return raw JSON only. No markdown.
        Keys: "overall_attendance" (float), "subjects" (list of floats), "raw_text" (string summary).
        Example: {"overall_attendance": 85.5, "subjects": [80.0, 90.5], "raw_text": "Found total 85.5%"}
        """

        # 5. Generate
        print("⏳ Sending request to Gemini...")
        response = model.generate_content([prompt, image])
        print("✅ Received response from Gemini.")
        
        # 6. Clean & Parse
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        
        try:
            parsed_data = json.loads(clean_text)
            # Update our result_data with what we found
            result_data.update(parsed_data)
        except json.JSONDecodeError:
            print(f"⚠️ JSON Parse Error. Raw text: {clean_text}")
            result_data["raw_text"] = f"Failed to parse JSON. Raw: {clean_text}"

    except Exception as e:
        # 7. Catch ALL errors so server doesn't crash
        error_msg = f"🔥 AI Error: {str(e)}"
        print(error_msg)
        result_data["raw_text"] = error_msg
    
    # 8. Always return a dict that matches the expected schema
    return result_data