import ollama

def clean_ocr_text(text):
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

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['message']['content']