import ollama
import json
import re

def clean_json(response_text):
    response_text = re.sub(r"```json|```", "", response_text).strip()
    return response_text

def parse_receipt(text):
    prompt = f"""
You are a strict JSON generator.

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
    
    def filter_fields(data):
        return {
            "company": data.get("company"),
            "date": data.get("date"),
            "time": data.get("time"),
            "items": data.get("items"),
            "total": data.get("total"),
            "tax": data.get("tax"),
            "payment_method": data.get("payment_method"),
    }
        


    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response['message']['content']
    cleaned = clean_json(raw)

    try:
        data = json.loads(cleaned)
        data = filter_fields(data)
        return data
    except:
        print("JSON parsing failed")
        print(cleaned)
        return None