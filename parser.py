import json
import re
import ollama


def extract_json_object(text):
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False

    for index, ch in enumerate(text[start:], start):
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]

    return None


def clean_json(response_text):
    response_text = re.sub(r"```json|```", "", response_text)
    response_text = re.sub(r"//.*", "", response_text).strip()
    extracted = extract_json_object(response_text)
    return extracted or response_text


def parse_float(value):
    if value is None:
        return 0.0
    try:
        candidate = str(value).strip().replace("€", "").replace("$", "").replace(",", ".")
        match = re.search(r"-?\d+(?:\.\d+)?", candidate)
        return float(match.group(0)) if match else 0.0
    except Exception:
        return 0.0


def normalize_items(items):
    if not isinstance(items, list):
        return []

    normalized = []
    for item in items:
        if not isinstance(item, dict):
            continue
        normalized.append({
            "name": str(item.get("name", "")).strip(),
            "price": parse_float(item.get("price", 0))
        })
    return normalized


def normalize_payment_method(value):
    if not isinstance(value, dict):
        return {"type": "", "card": ""}
    return {
        "type": str(value.get("type", "")).strip(),
        "card": str(value.get("card", "")).strip()
    }


def normalize_output(data):
    if not isinstance(data, dict):
        return None
    return {
        "company": str(data.get("company", "")).strip(),
        "date": str(data.get("date", "")).strip(),
        "time": str(data.get("time", "")).strip(),
        "items": normalize_items(data.get("items", [])),
        "total": parse_float(data.get("total", 0)),
        "tax": parse_float(data.get("tax", 0)),
        "payment_method": normalize_payment_method(data.get("payment_method", {}))
    }


def parse_receipt(text):
    prompt = f"""
You are a strict JSON generator.
This is a payment terminal receipt.
Do NOT hallucinate items.
If no item names exist, return empty items list.

Return ONLY JSON with EXACTLY these fields:
- company
- date
- time
- items (name + price)
- total
- tax
- payment_method (type, card)

DO NOT include any other fields.
DO NOT add extra keys.
DO NOT include comments inside JSON.

Format:
{{
  "company": "",
  "date": "",
  "time": "",
  "items": [{{"name": "", "price": 0}}],
  "total": 0,
  "tax": 0,
  "payment_method": {{"type": "", "card": ""}}
}}

Receipt:
{text}
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response["message"]["content"]
    cleaned = clean_json(raw)

    try:
        data = json.loads(cleaned)
        return normalize_output(data)
    except Exception as e:
        print("JSON parsing failed:", e)
        print(cleaned)
        return None