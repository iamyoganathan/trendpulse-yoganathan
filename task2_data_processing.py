import os

import pandas as pd


DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "trends_clean.csv")
CATEGORY_ORDER = ["technology", "worldnews", "sports", "science", "entertainment"]


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


def load_json_dataframe(json_path):
    """Load the collected trend stories into a pandas DataFrame."""
    return pd.read_json(json_path)


def clean_dataframe(frame):
    """Apply the assignment cleaning rules step by step."""
    cleaned = frame.copy()

    cleaned["title"] = cleaned["title"].astype("string").str.strip()
    cleaned["score"] = pd.to_numeric(cleaned["score"], errors="coerce")
    cleaned["num_comments"] = pd.to_numeric(cleaned["num_comments"], errors="coerce")
    cleaned["post_id"] = pd.to_numeric(cleaned["post_id"], errors="coerce")

    cleaned = cleaned.drop_duplicates(subset=["post_id"], keep="first")
    after_duplicates = len(cleaned)

    cleaned = cleaned.dropna(subset=["post_id", "title", "score"])
    after_nulls = len(cleaned)

    cleaned = cleaned[cleaned["score"] >= 5]
    after_low_scores = len(cleaned)

    cleaned["post_id"] = cleaned["post_id"].astype(int)
    cleaned["score"] = cleaned["score"].astype(int)
    cleaned["num_comments"] = cleaned["num_comments"].fillna(0).astype(int)

    cleaned = cleaned.sort_values(by=["category", "score", "post_id"], ascending=[True, False, True])
    cleaned = cleaned.reset_index(drop=True)

    return cleaned, after_duplicates, after_nulls, after_low_scores


def save_to_csv(frame, csv_path):
    """Write the cleaned DataFrame to CSV in the data folder."""
    os.makedirs(DATA_DIR, exist_ok=True)

    frame.to_csv(csv_path, index=False)


def print_category_summary(frame):
    """Print a quick story count by category."""
    print("\nStories per category:")
    counts = frame["category"].value_counts()
    for category in CATEGORY_ORDER:
        if category in counts:
            print(f"  {category:<16}{counts[category]}")


def main():
    json_path = find_latest_json_file()
    if not json_path:
        print("No trends JSON file found in the data folder.")
        return

    try:
        raw_frame = load_json_dataframe(json_path)
    except (OSError, ValueError, pd.errors.EmptyDataError) as exc:
        print(f"Failed to load JSON data: {exc}")
        return

    print(f"Loaded {len(raw_frame)} stories from {json_path}")

    cleaned_frame, after_duplicates, after_nulls, after_low_scores = clean_dataframe(raw_frame)

    print(f"After removing duplicates: {after_duplicates}")
    print(f"After removing nulls: {after_nulls}")
    print(f"After removing low scores: {after_low_scores}")

    save_to_csv(cleaned_frame, OUTPUT_FILE)

    print(f"\nSaved {len(cleaned_frame)} rows to {OUTPUT_FILE}")
    print_category_summary(cleaned_frame)


if __name__ == "__main__":
    main()