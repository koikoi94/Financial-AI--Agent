# file_handler.py
import uuid
from pathlib import Path
import fitz

def prepare_file(file_path, output_dir=None):
    output_dir = Path(output_dir) if output_dir is not None else Path("data")
    output_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file_path).suffix.lower()
    if ext in [".jpg", ".jpeg", ".png"]:
        return [file_path]

    if ext == ".pdf":
        image_paths = []

        with fitz.open(file_path) as pdf:
            for i, page in enumerate(pdf):
                matrix = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=matrix)
                output_path = output_dir / f"page_{i}_{uuid.uuid4().hex}.png"
                pix.save(str(output_path))
                image_paths.append(str(output_path))

        return image_paths

    raise ValueError("Unsupported file format")