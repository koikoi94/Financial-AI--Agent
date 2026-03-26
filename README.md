#  AI Agent for Financial Document Processing

## Overview

This project is an AI-powered pipeline for processing financial documents such as receipts and invoices. It combines OCR, text normalization, and intelligent parsing to extract structured information from unstructured data.

## Features

* OCR-based text extraction from receipts/images/PDFs
* Text cleaning and normalization
*  Intelligent parsing of financial data
*  Post-processing for structured output
*  Modular pipeline (cleaner → OCR → parser → postprocess)

##  Tech Stack

* Python
* OCR (Tesseract / similar)
* Regex & NLP techniques
* LLM-based post-processing 

##  Project Structure

```
├── main.py
├── cleaner.py
├── ocr.py
├── normalizer.py
├── parser.py
├── postprocess.py
├── requirements.txt
├── .gitignore
└── data/ (not included in repo)
```

##  How to Run

```bash
# create environment
python -m venv parsing

# activate
source parsing/Scripts/activate  # Windows Git Bash

# install dependencies
pip install -r requirements.txt

# run project
python main.py
```

## Data

Place your receipt images or PDFs inside the `data/` folder before running the project.


## Author

Chaiti Roy
