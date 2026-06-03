import easyocr

# Initialize EasyOCR once
reader = easyocr.Reader(['en'], gpu=False)


def extract_text(image_path):

    try:
        # OCR extraction
        results = reader.readtext(
            image_path,
            detail=0,
            paragraph=False
        )

        # Convert list to clean text
        extracted_text = "\n".join(results)

        return extracted_text

    except Exception as e:
        print("OCR ERROR:", e)
        return ""