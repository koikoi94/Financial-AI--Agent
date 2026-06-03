import json
import shutil
import tempfile
from pathlib import Path
from ocr import extract_text
from cleaner import clean_ocr_text
from parser import parse_receipt
from normalizer import normalize_ocr_text
from postprocess import postprocess_receipt
from file_handler import prepare_file
from preprocess import preprocess_image

def run_pipeline(image_path):
    temp_dir = Path(tempfile.mkdtemp(prefix="receipt_pipeline_"))
    page_images = []
    preprocessed_images = []

    try:
        files = prepare_file(image_path, temp_dir)
        page_images = files
        print("FILES:", files)
        raw_text = ""

        for file in files:
            print("PREPROCESSING FILE:", file)
            processed_image = preprocess_image(file, temp_dir)
            preprocessed_images.append(processed_image)

            print("PREPROCESSED IMAGE:", processed_image)
            text = extract_text(processed_image)
            print("OCR TEXT:")
            print(text)
            raw_text += "\n" + text

        filtered_text = "\n".join(
            line.strip() for line in raw_text.splitlines() if len(line.strip()) >= 3
        )

        cleaned_text = clean_ocr_text(filtered_text)
        normalized_text = normalize_ocr_text(cleaned_text or filtered_text)

        parsed = parse_receipt(normalized_text)
        parsed = postprocess_receipt(parsed, filtered_text)

        return parsed

    finally:
        for path in page_images + preprocessed_images:
            try:
                if Path(path).exists():
                    Path(path).unlink()
                    print(f"Cleaned up: {path}")
            except Exception as e:
                print(f"Warning: could not delete temp file {path}: {e}")

        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: could not remove temp directory {temp_dir}: {e}")
