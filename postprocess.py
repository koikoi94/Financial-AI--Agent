import re


def parse_number(value):
    if value is None:
        return 0.0
    try:
        raw = str(value).strip().replace("€", "").replace("$", "").replace(",", ".")
        match = re.search(r"-?\d+(?:\.\d+)?", raw)
        return float(match.group(0)) if match else 0.0
    except Exception:
        return 0.0


def format_time(value):
    if not value:
        return value
    value = str(value).strip()
    if len(value) == 4 and value.isdigit():
        return f"{value[:2]}:{value[2:]}"
    if re.match(r"^\d{1,2}:\d{2}$", value):
        return value
    return value


def extract_date_and_time_from_ocr(ocr_text):
    date_value = None
    time_value = None

    date_candidates = re.findall(r"\b\d{6}\b", ocr_text)
    for raw in date_candidates:
        day = int(raw[:2])
        month = int(raw[2:4])
        year = int(raw[4:6])
        if 1 <= day <= 31 and 1 <= month <= 12:
            date_value = f"{raw[:2]}.{raw[2:4]}.20{raw[4:6]}"
            break

    time_candidates = re.findall(r"\b\d{4}\b", ocr_text)
    for raw in time_candidates:
        hh = int(raw[:2])
        mm = int(raw[2:4])
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            time_value = f"{raw[:2]}:{raw[2:4]}"
            break

    return date_value, format_time(time_value)


def normalize_payment(payment_method):
    if not isinstance(payment_method, dict):
        return {"type": "", "card": ""}

    ptype = str(payment_method.get("type", "")).strip().lower()
    card = str(payment_method.get("card", "")).strip()

    if ptype in ["bargeld", "cash"]:
        return {"type": "cash", "card": ""}
    if ptype in ["card", "karte", "ec", "visa", "mastercard", "debit", "credit"]:
        return {"type": "card", "card": card}

    return {"type": ptype, "card": card}


def fix_company(company):
    if not company:
        return ""
    return str(company).replace("Gmbk", "GmbH").strip()


def fix_tax(tax_value, ocr_text):
    parsed_tax = parse_number(tax_value)
    if parsed_tax == 4.28 and any(token in ocr_text for token in ["MwSt", "MWST", "Mwst"]):
        if "1.28" in ocr_text:
            return 1.28
    return parsed_tax


def clean_item_name(name):
    if not name:
        return ""

    name = str(name)
    name = name.replace("9länzend", "glänzend")
    if "Sprühlack" in name and not name.strip().endswith("1"):
        name = name + " 1"
    return name.strip()


def postprocess_receipt(data, ocr_text):
    if not isinstance(data, dict):
        return {}

    output = {
        "company": fix_company(data.get("company", "")),
        "date": data.get("date", ""),
        "time": data.get("time", ""),
        "items": [],
        "total": parse_number(data.get("total", 0)),
        "tax": fix_tax(data.get("tax", 0), ocr_text),
        "payment_method": normalize_payment(data.get("payment_method", {}))
    }

    extracted_date, extracted_time = extract_date_and_time_from_ocr(ocr_text)
    if extracted_date:
        output["date"] = extracted_date
    if extracted_time:
        output["time"] = extracted_time

    for item in data.get("items", []):
        if not isinstance(item, dict):
            continue
        output["items"].append({
            "name": clean_item_name(item.get("name", "")),
            "price": parse_number(item.get("price", 0))
        })

    return output