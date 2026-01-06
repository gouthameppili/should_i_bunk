import os
import json
import base64
import re
from groq import Groq

# Setup Groq Client
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def extract_attendance_from_image(file_bytes: bytes):
    result_data = {"overall_attendance": 0.0, "subjects": [], "raw_text": ""}

    if not client:
        print("❌ Groq API Key missing! Check Environment Variables.")
        return result_data

    try:
        # 1. Convert Image to Base64
        base64_image = base64.b64encode(file_bytes).decode('utf-8')
        
        # 2. Ask Llama 4 Scout (The new Vision Standard)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Look at the bottom right of this table. Find the 'TOTAL' percentage. Return ONLY the number (e.g., 92.16)."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            # 🟢 UPDATED MODEL ID: Llama 4 Scout (Replaces Llama 3.2 Vision)
            model="meta-llama/llama-4-scout-17b-16e-instruct", 
            temperature=0,
        )

        # 3. Get the Response
        content = chat_completion.choices[0].message.content
        print(f"🦙 Llama 4 Output: {content}")
        
        # 4. Extract the Number (Robust Regex)
        matches = re.findall(r"(\d+\.\d+)", content)
        
        if matches:
            percent = float(matches[-1])
            if 0 <= percent <= 100:
                result_data["overall_attendance"] = percent
                result_data["raw_text"] = content
                return result_data

        # Fallback for Integers
        int_matches = re.findall(r"(\d+)", content)
        if int_matches:
             valid_ints = [int(x) for x in int_matches if 50 <= int(x) <= 100]
             if valid_ints:
                 result_data["overall_attendance"] = float(valid_ints[-1])

        return result_data

    except Exception as e:
        print(f"🔥 Llama OCR Error: {str(e)}")
        # Fallback to Manual Entry prompt on frontend if specific error
        return {"overall_attendance": 0.0, "error": "AI Model Error. Please enter manually."}