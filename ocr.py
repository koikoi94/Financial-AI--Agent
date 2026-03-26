import easyocr
from PIL import Image, ImageFilter, ImageOps
import os

reader = easyocr.Reader(['en', 'de'])

def preprocess_image(image_path):
    img = Image.open(image_path).convert("L")   # grayscale
    #img = img.resize((img.width * 2, img.height * 2))  # enlarge
     # resize if too large
    max_size = 2000
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size))
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageOps.autocontrast(img)

    os.makedirs("data", exist_ok=True)
    processed_path = "data/temp_processed.png"
    img.save(processed_path)

    return processed_path

def extract_text(image_path):
    processed_path = preprocess_image(image_path)
    results = reader.readtext(processed_path, detail=0)
    return "\n".join(results)