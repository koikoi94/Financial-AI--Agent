import ollama


def clean_ocr_text(text):
    if not text or not text.strip():
        return ""

    prompt = f"""
You are a text cleaner.

Fix OCR errors in the following receipt text:
- correct spelling (German + English)
- fix numbers (7,99 → 7.99)
- fix words like Gmbk → GmbH
- keep structure similar

Do NOT summarize.
Do NOT remove important information.
Return ONLY cleaned text.

Text:
{text}
"""

    try:
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()
    except Exception as e:
        print("Cleaner model error:", e)
        return text.strip()