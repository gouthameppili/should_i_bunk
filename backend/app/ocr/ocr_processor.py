import google.generativeai as genai
import os
import json
from io import BytesIO
from PIL import Image

# Configure API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# --- 🧠 NEW: AUTO-SELECT THE BEST AVAILABLE MODEL ---
def get_best_available_model():
    try:
        # 1. Ask Google what models are available for this Key
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        print(f"📋 Available Models found: {available_models}")

        # 2. Priority List (Fastest to Slowest)
        priority_list = [
            "gemini-2.0-flash-exp",
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash-001",
            "gemini-1.5-pro",
            "gemini-pro-vision"
        ]

        # 3. Pick the first match
        for priority in priority_list:
            for model_name in available_models:
                # Check if the priority string is part of the official name (e.g. "models/gemini-1.5-flash")
                if priority in model_name:
                    print(f"✅ Selected Model: {model_name}")
                    return model_name
        
        # 4. If no specific match, take the first Gemini model found
        if available_models:
            return available_models[0]
            
    except Exception as e:
        print(f"⚠️ Model List Error: {e}")
    
    # Absolute Fallback if listing fails
    return "gemini-1.5-flash"

# Cache the model name so we don't list-models every single request
CURRENT_MODEL_NAME = get_best_available_model()

def extract_attendance_from_image(file_bytes: bytes):
    result_data = {"overall_attendance": 0.0, "subjects": [], "raw_text": ""}

    try:
        image = Image.open(BytesIO(file_bytes))
        
        # Use the auto-selected model
        model = genai.GenerativeModel(CURRENT_MODEL_NAME)

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
        print(f"🔥 OCR Error ({CURRENT_MODEL_NAME}): {str(e)}")
        return result_data