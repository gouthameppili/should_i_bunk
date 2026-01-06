import os
import json
import base64
import re
from groq import Groq  # 👈 New Library

# Setup Groq Client
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def extract_attendance_from_image(file_bytes: bytes):
    result_data = {"overall_attendance": 0.0, "subjects": [], "raw_text": ""}

    if not client:
        print("❌ Groq API Key missing! Check Environment Variables.")
        return result_data

    try:
        # 1. Convert Image to Base64 (Groq requires this format)
        base64_image = base64.b64encode(file_bytes).decode('utf-8')
        
        # 2. Ask Llama 3.2 Vision
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract the 'TOTAL' percentage from the bottom right of this table. Return ONLY the number (e.g. 92.16). Do not write sentences."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="llama-3.2-11b-vision-preview", # 👈 The Vision Model
            temperature=0, # Be precise, not creative
        )

        # 3. Get the Response
        content = chat_completion.choices[0].message.content
        print(f"🦙 Llama Output: {content}")
        
        # 4. Extract the Number (Robust Regex)
        # Finds the last number in the response that contains a decimal
        # Matches: 92.16, 85.5, etc.
        matches = re.findall(r"(\d+\.\d+)", content)
        
        if matches:
            # Usually the percentage is the last number mentioned or the only one
            percent = float(matches[-1])
            if 0 <= percent <= 100:
                result_data["overall_attendance"] = percent
                result_data["raw_text"] = content
                return result_data

        # Fallback for Integers (if attendance is exactly 92%)
        int_matches = re.findall(r"(\d+)", content)
        if int_matches:
             # Filter logic: Attendance is usually > 50 and <= 100
             valid_ints = [int(x) for x in int_matches if 50 <= int(x) <= 100]
             if valid_ints:
                 result_data["overall_attendance"] = float(valid_ints[-1])

        return result_data

    except Exception as e:
        print(f"🔥 Llama OCR Error: {str(e)}")
        return result_data