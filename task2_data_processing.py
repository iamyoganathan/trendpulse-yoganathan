import argparse
import csv
import json
import os


DATA_DIR = "data"


def find_latest_json_file(data_dir=DATA_DIR):
    """Return the newest trends JSON file in the data folder."""
    if not os.path.isdir(data_dir):
        return None

    candidates = []
    for name in os.listdir(data_dir):
        if name.startswith("trends_") and name.endswith(".json"):
            candidates.append(os.path.join(data_dir, name))

    if not candidates:
        return None

    return max(candidates, key=os.path.getmtime)


def load_json_records(json_path):
    """Load the collected trend stories from JSON."""
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of records.")

    return data


def clean_record(record):
    """Normalize a single record and keep only the required CSV fields."""
    post_id = record.get("post_id")
    title = str(record.get("title", "")).strip()
    category = str(record.get("category", "")).strip().lower()
    score = record.get("score", 0)
    num_comments = record.get("num_comments", 0)
    author = str(record.get("author", "")).strip()
    collected_at = str(record.get("collected_at", "")).strip()

    if post_id is None or not title or not category:
        return None

    try:
        post_id = int(post_id)
    except (TypeError, ValueError):
        return None

    try:
        score = int(score)
    except (TypeError, ValueError):
        score = 0

    try:
        num_comments = int(num_comments)
    except (TypeError, ValueError):
        num_comments = 0

    return {
        "post_id": post_id,
        "title": title,
        "category": category,
        "score": score,
        "num_comments": num_comments,
        "author": author,
        "collected_at": collected_at,
    }


def clean_records(records):
    """Remove invalid rows and standardize values while keeping category-level rows intact."""
    cleaned = []

    for record in records:
        if not isinstance(record, dict):
            continue

        cleaned_record = clean_record(record)
        if cleaned_record is None:
            continue
        cleaned.append(cleaned_record)

    # Keep the output stable and easy to inspect.
    cleaned.sort(key=lambda item: (item["category"], -item["score"], item["post_id"]))
    return cleaned


def build_output_path(input_json_path):
    """Create a CSV name that matches the source file date."""
    base_name = os.path.splitext(os.path.basename(input_json_path))[0]
    suffix = base_name.replace("trends_", "")
    return os.path.join(DATA_DIR, f"cleaned_trends_{suffix}.csv")


def save_to_csv(records, csv_path):
    """Write cleaned records to CSV in the data folder."""
    os.makedirs(DATA_DIR, exist_ok=True)

    fieldnames = [
        "post_id",
        "title",
        "category",
        "score",
        "num_comments",
        "author",
        "collected_at",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def parse_args():
    """Parse optional input and output paths from the command line."""
    parser = argparse.ArgumentParser(description="Clean TrendPulse JSON data and save it as CSV.")
    parser.add_argument("json_path", nargs="?", help="Path to the input trends JSON file.")
    parser.add_argument("--output", help="Optional output CSV path.")
    return parser.parse_args()


def main():
    args = parse_args()

    json_path = args.json_path or find_latest_json_file()
    if not json_path:
        print("No trends JSON file found in the data folder.")
        return

    try:
        raw_records = load_json_records(json_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Failed to load JSON data: {exc}")
        return

    cleaned_records = clean_records(raw_records)

    output_path = args.output or build_output_path(json_path)
    save_to_csv(cleaned_records, output_path)

    print(f"Cleaned {len(cleaned_records)} stories. Saved to {output_path}")


if __name__ == "__main__":
    main()