"""
Batch receipt processor for handling multiple files from a directory.
Supports: PDF, PNG, JPG, JPEG
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

from app.pipeline import run_pipeline

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


@dataclass
class ProcessingResult:
    """Result of processing a single receipt file."""
    filename: str
    status: str  # "success", "error", "skipped"
    output: dict = None
    error_message: str = None

    def to_dict(self) -> dict:
        return asdict(self)


class BatchReceiptProcessor:
    """Process multiple receipt files from a directory."""

    def __init__(self, input_dir: str, output_dir: str = None):
        """
        Initialize batch processor.
        
        Args:
            input_dir: Directory containing receipt files
            output_dir: Directory to save parsed JSON outputs (defaults to input_dir/outputs)
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir) if output_dir else self.input_dir / "outputs"
        
        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {self.input_dir}")
        
        if not self.input_dir.is_dir():
            raise ValueError(f"Input path is not a directory: {self.input_dir}")
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir}")

    def get_supported_files(self) -> List[Path]:
        """
        Scan input directory for supported receipt files.
        
        Returns:
            List of file paths with supported extensions
        """
        files = []
        for file_path in self.input_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(file_path)
        return sorted(files)

    def process_single_file(self, file_path: Path) -> ProcessingResult:
        """
        Process a single receipt file.
        
        Args:
            file_path: Path to receipt file
            
        Returns:
            ProcessingResult with parsed data or error info
        """
        try:
            logger.info(f"Processing: {file_path.name}")
            
            # Run pipeline
            parsed = run_pipeline(str(file_path))
            
            if parsed is None:
                return ProcessingResult(
                    filename=file_path.name,
                    status="error",
                    error_message="Pipeline returned None"
                )
            
            # Save to JSON
            output_file = self.output_dir / f"{file_path.stem}_parsed.json"
            output_file.write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")
            
            logger.info(f"✓ Saved: {output_file.name}")
            
            return ProcessingResult(
                filename=file_path.name,
                status="success",
                output=parsed
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"✗ Failed {file_path.name}: {error_msg}")
            
            return ProcessingResult(
                filename=file_path.name,
                status="error",
                error_message=error_msg
            )

    def process_batch(self) -> Tuple[List[ProcessingResult], Dict]:
        """
        Process all supported files in input directory.
        
        Returns:
            Tuple of (results list, summary dict)
        """
        files = self.get_supported_files()
        
        if not files:
            logger.warning(f"No supported files found in {self.input_dir}")
            return [], {"total": 0, "success": 0, "error": 0, "skipped": 0}
        
        logger.info(f"Found {len(files)} file(s) to process")
        results = []
        
        for file_path in files:
            result = self.process_single_file(file_path)
            results.append(result)
        
        # Generate summary
        summary = {
            "total": len(results),
            "success": sum(1 for r in results if r.status == "success"),
            "error": sum(1 for r in results if r.status == "error"),
            "skipped": sum(1 for r in results if r.status == "skipped"),
            "output_directory": str(self.output_dir)
        }
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Batch Processing Summary")
        logger.info(f"{'='*50}")
        logger.info(f"Total: {summary['total']}")
        logger.info(f"Success: {summary['success']}")
        logger.info(f"Errors: {summary['error']}")
        logger.info(f"Output folder: {self.output_dir}")
        logger.info(f"{'='*50}")
        
        return results, summary

    def save_batch_report(self, results: List[ProcessingResult]) -> Path:
        """
        Save batch processing report as JSON.
        
        Args:
            results: List of ProcessingResult objects
            
        Returns:
            Path to report file
        """
        report = {
            "total_files": len(results),
            "successful": sum(1 for r in results if r.status == "success"),
            "failed": sum(1 for r in results if r.status == "error"),
            "files": [r.to_dict() for r in results]
        }
        
        report_file = self.output_dir / "batch_report.json"
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Report saved: {report_file}")
        
        return report_file


def main():
    """CLI interface for batch processing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Batch process receipt files from a directory"
    )
    parser.add_argument("input_dir", help="Directory containing receipt files")
    parser.add_argument(
        "--output",
        "-o",
        help="Output directory for parsed JSON (default: input_dir/outputs)",
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        processor = BatchReceiptProcessor(args.input_dir, args.output)
        results, summary = processor.process_batch()
        processor.save_batch_report(results)
        
        if summary["error"] > 0:
            exit(1)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
