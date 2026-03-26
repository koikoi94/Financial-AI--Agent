from ocr import extract_text
from cleaner import clean_ocr_text
from parser import parse_receipt
from normalizer import normalize_ocr_text
from postprocess import postprocess_receipt
import json

image_path = "data/scan0083.jpg"   # change if needed

# Step 1: OCR
text = extract_text(image_path)

# Step 2: Clean (LLM)
cleaned_text = clean_ocr_text(text)
print("CLEANED TEXT:\n", cleaned_text)

# Step 3: Normalize (RULES)
cleaned_text = normalize_ocr_text(cleaned_text)
print("NORMALIZED TEXT:\n", cleaned_text)

# Step 4: Parse (LLM → JSON)
parsed = parse_receipt(cleaned_text)

# Step 5: Postprocess (FIX OUTPUT)
parsed = postprocess_receipt(parsed, cleaned_text)

print("\nPARSED OUTPUT:\n", parsed)

# Step 6: Save JSON
if parsed:
    with open("output.json", "w") as f:
        json.dump(parsed, f, indent=4)
    print("JSON saved as output.json")
else:
    print(" Parsing failed, no JSON saved")
