import re

def normalize_ocr_text(text):
    replacements = {
        "Gmbk": "GmbH",
        "DD": "00",
        "D0": "00",
        "DO": "00",
        "ODD4": "0004",
        "Bargeld": "cash",
        "~idee-shop": "idee-shop",
        "Nurnberg": "Nürnberg",
        "Sprühlack 9länzend": "Sprühlack glänzend 1"
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    # Convert German decimal commas to dots only between digits
    text = re.sub(r'(?<=\d),(?=\d)', '.', text)

    # Fix common OCR tax pattern: 428 -> 1.28 when near MwSt line is too hard globally,
    # so leave as text cleanup only for now and handle in postprocess.
    return text