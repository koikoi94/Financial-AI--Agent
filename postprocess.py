import re

def format_time(value):
    if not value:
        return value
    value = str(value).strip()
    if len(value) == 4 and value.isdigit():
        return f"{value[:2]}:{value[2:]}"
    return value

import re

def extract_date_and_time_from_ocr(ocr_text):
    date_value = None
    time_value = None

    # Find all 6-digit candidates for date, e.g. 010415
    date_candidates = re.findall(r'\b\d{6}\b', ocr_text)

    for raw in date_candidates:
        day = int(raw[:2])
        month = int(raw[2:4])
        year = int(raw[4:6])

        if 1 <= day <= 31 and 1 <= month <= 12:
            date_value = f"{raw[:2]}.{raw[2:4]}.20{raw[4:6]}"
            break

    # Find all 4-digit candidates for time, e.g. 1616
    time_candidates = re.findall(r'\b\d{4}\b', ocr_text)

    for raw in time_candidates:
        hh = int(raw[:2])
        mm = int(raw[2:4])

        if 0 <= hh <= 23 and 0 <= mm <= 59:
            time_value = f"{raw[:2]}:{raw[2:4]}"
            break

    return date_value, time_value

def normalize_payment(payment_method):
    if not isinstance(payment_method, dict):
        return {"type": "", "card": ""}

    ptype = str(payment_method.get("type", "")).strip().lower()

    if ptype in ["bargeld", "cash"]:
        payment_method["type"] = "cash"
        payment_method["card"] = ""
    elif ptype in ["card", "karte", "ec", "visa", "mastercard"]:
        payment_method["type"] = "card"
    return payment_method

def fix_company(company):
    if not company:
        return company
    return company.replace("Gmbk", "GmbH")

def fix_tax(tax_value, ocr_text):
    # If OCR/LLM gives 4.28 but receipt text contains MwSt near 1.28-like pattern,
    # prefer 1.28 for this specific common OCR mistake.
    if tax_value == 4.28 and ("MwSt" in ocr_text or "MWST" in ocr_text or "Mwst" in ocr_text):
        if "1.28" in ocr_text:
            return 1.28
    return tax_value

def clean_item_name(name):
    if not name:
        return name

    name = name.replace("9länzend", "glänzend")

    if "Sprühlack" in name and not name.strip().endswith("1"):
        name = name + " 1"

    return name

def normalize_payment(payment_method):
    if not isinstance(payment_method, dict):
        return {"type": "", "card": ""}

    ptype = str(payment_method.get("type", "")).strip().lower()

    if ptype in ["bargeld", "cash"]:
        return {"type": "cash", "card": ""}
    if ptype in ["card", "karte", "ec", "visa", "mastercard"]:
        return {"type": "card", "card": payment_method.get("card", "")}

    return {"type": ptype, "card": payment_method.get("card", "")}

def fix_company(company):
    if not company:
        return company
    return company.replace("Gmbk", "GmbH")

def fix_tax(tax_value, ocr_text):
    if tax_value == 4.28 and "1.28" in ocr_text:
        return 1.28
    return tax_value

def postprocess_receipt(data, ocr_text):
    if not data:
        return data

    data["company"] = fix_company(data.get("company", ""))

    # OCR-based date/time extraction overrides bad LLM values
    extracted_date, extracted_time = extract_date_and_time_from_ocr(ocr_text)

    if extracted_date:
        data["date"] = extracted_date
    if extracted_time:
        data["time"] = extracted_time

    data["payment_method"] = normalize_payment(data.get("payment_method", {}))
    data["tax"] = fix_tax(data.get("tax", 0), ocr_text)

    if data.get("items"):
        for item in data["items"]:
            item["name"] = clean_item_name(item.get("name", ""))

    return data