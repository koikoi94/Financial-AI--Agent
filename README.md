[![CI](https://github.com/koikoi94/Financial-AI--Agent/actions/workflows/ci.yml/badge.svg)](https://github.com/koikoi94/Financial-AI--Agent/actions/workflows/ci.yml)

# AI Agent for Financial Document Processing

## Overview

AI-powered financial document processing system that extracts structured information from receipts and invoices in PDF and image formats.

The project combines OCR, OpenCV-based image preprocessing, LLM-powered text cleaning, and intelligent parsing to transform unstructured financial documents into structured JSON data through a FastAPI REST API.

---

## Features

* Receipt and invoice processing
* PDF and image upload support
* PDF-to-image conversion using PyMuPDF
* OpenCV-based image preprocessing
* OCR-based text extraction
* LLM-powered OCR correction and text cleaning
* Intelligent financial data extraction
* Structured JSON output generation
* Batch document processing
* FastAPI REST API
* Interactive Swagger API documentation

---

## System Architecture

```text
Receipt / Invoice (PDF, JPG, PNG)
                │
                ▼
      PyMuPDF PDF Conversion
                │
                ▼
      OpenCV Image Preprocessing
                │
                ▼
          OCR Extraction
                │
                ▼
      LLM Text Cleaning (Ollama)
                │
                ▼
      Financial Data Parsing
                │
                ▼
         JSON Generation
                │
                ▼
        FastAPI Response
```

---

## Tech Stack

* Python
* FastAPI
* OpenCV
* OCR
* Ollama
* Mistral
* PyMuPDF
* JSON Processing
* Git & GitHub

---

## Project Structure

```text
Financial-AI-Agent/
│
├── app/
│   ├── main.py
│   └── pipeline.py
│
├── cleaner.py
├── file_handler.py
├── normalizer.py
├── ocr.py
├── parser.py
├── postprocess.py
├── preprocess.py
├── batch_processor.py
├── validate_receipt.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/koikoi94/Financial-AI--Agent.git
cd Financial-AI--Agent
```

### Create Virtual Environment

```bash
python -m venv parsing
```

### Activate Environment

Git Bash:

```bash
source parsing/Scripts/activate
```

Windows CMD:

```cmd
parsing\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the API

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

API URL:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoint

### Parse Financial Document

```http
POST /parse-receipt
```

### Input

* PDF
* JPG
* JPEG
* PNG

### Output Example

```json
{
  "company": "STEMA POWER",
  "date": "04.04.2013",
  "time": "14:30",
  "items": [
    {
      "name": "Battery Terminal Clamp",
      "price": 18.89
    }
  ],
  "total": 18.89,
  "tax": 3.02,
  "payment_method": {
    "type": "paypal",
    "card": ""
  }
}
```

---

## Workflow

1. Upload a receipt or invoice.
2. Convert PDF pages into images using PyMuPDF.
3. Preprocess images using OpenCV.
4. Extract text using OCR.
5. Clean OCR output using Ollama and Mistral.
6. Normalize extracted text.
7. Parse financial information into structured fields.
8. Generate JSON output.
9. Return results through the FastAPI API.

---

## Future Improvements

* Improve OCR accuracy for scanned invoices
* Confidence scoring for extracted fields
* Multi-language support
* Docker deployment
* Database integration
* Enhanced receipt validation rules
* Advanced financial document classification
* Cloud deployment

---

## Author

**Chaiti Roy**

M.Sc. Data Science,
Friedrich-Alexander-Universität Erlangen-Nürnberg (FAU)
