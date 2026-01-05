import easyocr
import numpy as np
import cv2
from io import BytesIO
from PIL import Image

# --- LAZY LOADING SETUP ---
# We do NOT initialize the reader here. We set it to None.
reader_instance = None

def get_reader():
    """
    Only loads the heavy AI model when absolutely necessary.
    """
    global reader_instance
    if reader_instance is None:
        print("🐢 Loading OCR Model for the first time... (This might be slow)")
        # gpu=False is CRITICAL for Render Free Tier
        reader_instance = easyocr.Reader(['en'], gpu=False, verbose=False)
    return reader_instance

def extract_attendance_from_image(file_bytes: bytes):
    # 1. Convert bytes to image
    image = Image.open(BytesIO(file_bytes))
    image_np = np.array(image)

    # 2. Get the Reader (Loads model now if not loaded yet)
    reader = get_reader()

    # 3. Perform Text Extraction
    results = reader.readtext(image_np)
    
    # 4. Process Results (Your existing logic)
    text_lines = []
    for (bbox, text, prob) in results:
        if prob > 0.3:
            text_lines.append(text.lower())
            
    full_text = " ".join(text_lines)
    
    # --- YOUR LOGIC TO EXTRACT NUMBERS ---
    import re
    # Find all percentages (e.g., "85.5", "90")
    numbers = re.findall(r"(\d+(?:\.\d+)?)", full_text)
    
    valid_attendance = []
    for num in numbers:
        try:
            val = float(num)
            if 0 <= val <= 100:
                valid_attendance.append(val)
        except:
            continue
            
    # Simple Heuristic: The Overall attendance is usually the last or one of the numbers found
    # If we found nothing, return 0
    overall = valid_attendance[-1] if valid_attendance else 0.0
    
    return {
        "raw_text": full_text[:100] + "...", 
        "overall_attendance": overall,
        "subjects": valid_attendance
    }