import easyocr
import re

reader = easyocr.Reader(['en'], gpu=False)

def extract_attendance_from_image(image_bytes):
    print("👀 Scanning image with 'Bottom-Right' Logic...")
    
    # 1. Read text 
    # detail=0 returns a simple list of strings found
    results = reader.readtext(image_bytes, detail=0)
    
    full_text = " ".join(results)
    print(f"📝 Raw Text: {full_text[:100]}...") 

    overall_attendance = 0.0
    subject_attendances = []

    # 2. Extract ALL decimal numbers (percentages) from the entire page
    # Pattern: 1 to 3 digits, dot, 2 digits (e.g., 93.55, 87.50, .00)
    # The regex looks for: "Number.Number" OR ".Number"
    raw_decimals = re.findall(r"\b(\d{1,3}\.\d{2})\b|\b(\.\d{2})\b", full_text)
    
    clean_numbers = []
    for match in raw_decimals:
        # Regex returns tuples like ('93.55', '') or ('', '.00'). We pick the non-empty one.
        num_str = match[0] if match[0] else match[1]
        try:
            val = float(num_str)
            if 0 <= val <= 100.0:
                clean_numbers.append(val)
        except:
            continue
            
    if not clean_numbers:
        return 0.0, []

    print(f"🔢 All Numbers Found: {clean_numbers}")

    # --- NEW LOGIC: Position Based ---
    # In your report, the Total is ALWAYS the last number in the list.
    
    overall_attendance = clean_numbers[-1] # Take the last one
    
    # All numbers BEFORE the last one are considered 'Subjects'
    subject_attendances = clean_numbers[:-1] 

    print(f"✅ Final Decision -> Overall: {overall_attendance}, Subjects: {subject_attendances}")
    
    return overall_attendance, subject_attendances