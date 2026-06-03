import gc
import shutil
import time
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.pipeline import run_pipeline
from batch_processor import BatchReceiptProcessor

app = FastAPI()
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Receipt Parser API Running"}

@app.post("/parse-receipt")
async def parse_receipt_endpoint(file: UploadFile = File(...)):
    # Generate unique filename to avoid conflicts
    file_ext = Path(file.filename or "receipt").suffix or ".pdf"
    unique_name = f"{uuid.uuid4().hex}_{int(time.time())}{file_ext}"
    file_path = DATA_DIR / unique_name

    # Write uploaded file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except PermissionError:
        raise HTTPException(status_code=500, detail="Permission denied writing to data directory")
    finally:
        await file.close()

    try:
        result = run_pipeline(str(file_path))
        if result is None:
            raise HTTPException(status_code=500, detail="Receipt parsing failed")
        return result
    finally:
        gc.collect()
        for attempt in range(3):
            try:
                if file_path.exists():
                    file_path.unlink()
                break
            except PermissionError:
                time.sleep(0.5)


class BatchProcessRequest(BaseModel):
    input_dir: str
    output_dir: str = None


@app.post("/batch-parse-receipts")
def batch_parse_receipts(request: BatchProcessRequest):
    """
    Process all receipt files in a directory.
    
    Supported formats: PDF, PNG, JPG, JPEG
    
    Returns:
        - results: List of processing results per file
        - summary: Statistics (total, success, error counts)
    """
    try:
        processor = BatchReceiptProcessor(request.input_dir, request.output_dir)
        results, summary = processor.process_batch()
        processor.save_batch_report(results)
        
        return {
            "summary": summary,
            "results": [r.to_dict() for r in results]
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")
