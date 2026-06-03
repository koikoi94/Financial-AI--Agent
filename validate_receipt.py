import argparse
import json
import sys
from pathlib import Path

try:
    from app.pipeline import run_pipeline
except ModuleNotFoundError as e:
    missing = e.name
    print("Error: required module is missing:", missing)
    print("Please run this script using the project virtual environment.")
    print(r"Example: parsing\Scripts\python.exe validate_receipt.py path/to/receipt.pdf")
    print(r"Current python executable: " + sys.executable)
    sys.exit(1)

EXPECTED_SCHEMA = {
    "company": str,
    "date": str,
    "time": str,
    "items": list,
    "total": (int, float),
    "tax": (int, float),
    "payment_method": dict,
}


def validate_output(data):
    if not isinstance(data, dict):
        return ["Parsed result is not a JSON object."]

    issues = []
    for key, expected_type in EXPECTED_SCHEMA.items():
        if key not in data:
            issues.append(f"Missing field: {key}")
            continue
        if not isinstance(data[key], expected_type):
            issues.append(
                f"Field '{key}' has wrong type: expected {expected_type}, got {type(data[key]).__name__}"
            )

    if isinstance(data.get("items"), list):
        for index, item in enumerate(data["items"]):
            if not isinstance(item, dict):
                issues.append(f"Item {index} is not an object.")
                continue
            if "name" not in item or "price" not in item:
                issues.append(f"Item {index} must contain 'name' and 'price'.")
                continue
            if not isinstance(item["name"], str):
                issues.append(f"Item {index} name must be a string.")
            if not isinstance(item["price"], (int, float)):
                issues.append(f"Item {index} price must be a number.")

    if isinstance(data.get("payment_method"), dict):
        if "type" not in data["payment_method"] or "card" not in data["payment_method"]:
            issues.append("payment_method must contain 'type' and 'card'.")

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse a receipt image or PDF and validate the parsed JSON output."
    )
    parser.add_argument("receipt", help="Path to receipt image or PDF file")
    parser.add_argument(
        "--output",
        "-o",
        help="Optional path to save parsed JSON output",
        default=None,
    )
    args = parser.parse_args()

    receipt_path = Path(args.receipt)
    if not receipt_path.exists():
        raise SystemExit(f"Receipt file does not exist: {receipt_path}")

    print(f"Parsing receipt: {receipt_path}")
    result = run_pipeline(str(receipt_path))

    if result is None:
        raise SystemExit("Receipt parsing returned no result.")

    pretty = json.dumps(result, indent=2, ensure_ascii=False)
    print("\nParsed output:\n")
    print(pretty)

    if args.output:
        Path(args.output).write_text(pretty, encoding="utf-8")
        print(f"\nSaved parsed JSON to: {args.output}")

    issues = validate_output(result)
    if issues:
        print("\nValidation issues detected:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit("Validation failed.")

    print("\nValidation passed: output matches expected receipt schema.")


if __name__ == "__main__":
    main()
