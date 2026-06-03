import cv2
import uuid
from pathlib import Path


def preprocess_image(image_path, output_dir=None):
    output_dir = Path(output_dir) if output_dir is not None else Path("data")
    output_dir.mkdir(parents=True, exist_ok=True)

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    scale_percent = 200
    width = int(gray.shape[1] * scale_percent / 100)
    height = int(gray.shape[0] * scale_percent / 100)

    gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        15
    )

    output_path = output_dir / f"preprocessed_{uuid.uuid4().hex}.png"
    cv2.imwrite(str(output_path), thresh)

    return str(output_path)
