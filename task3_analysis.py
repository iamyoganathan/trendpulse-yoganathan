import argparse
import json
import os
from datetime import datetime

import numpy as np
import pandas as pd


DATA_DIR = "data"


def find_latest_cleaned_csv(data_dir=DATA_DIR):
    """Return the newest cleaned CSV file in the data folder."""
    if not os.path.isdir(data_dir):
        return None

    candidates = []
    for name in os.listdir(data_dir):
        if name.startswith("cleaned_trends_") and name.endswith(".csv"):
            candidates.append(os.path.join(data_dir, name))

    if not candidates:
        return None

    return max(candidates, key=os.path.getmtime)


def load_data(csv_path):
    """Load the cleaned CSV into a pandas DataFrame."""
    df = pd.read_csv(csv_path)

    required_columns = {
        "post_id",
        "title",
        "category",
        "score",
        "num_comments",
        "author",
        "collected_at",
    }
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    return df


def clean_dataframe(df):
    """Apply final analysis-ready cleaning and type conversion."""
    frame = df.copy()

    frame["category"] = frame["category"].astype(str).str.strip().str.lower()
    frame["title"] = frame["title"].astype(str).str.strip()
    frame["author"] = frame["author"].astype(str).str.strip()
    frame["collected_at"] = frame["collected_at"].astype(str).str.strip()

    frame["score"] = pd.to_numeric(frame["score"], errors="coerce").fillna(0).astype(int)
    frame["num_comments"] = pd.to_numeric(frame["num_comments"], errors="coerce").fillna(0).astype(int)
    frame["post_id"] = pd.to_numeric(frame["post_id"], errors="coerce").astype("Int64")

    frame = frame.dropna(subset=["post_id", "title", "category"])
    frame = frame.drop_duplicates(subset=["post_id"]).reset_index(drop=True)

    return frame


def build_category_summary(df):
    """Compute category-level metrics for reporting and visualization."""
    grouped = df.groupby("category", dropna=False)

    summary = grouped.agg(
        story_count=("post_id", "count"),
        avg_score=("score", "mean"),
        median_score=("score", "median"),
        max_score=("score", "max"),
        avg_comments=("num_comments", "mean"),
        total_comments=("num_comments", "sum"),
        unique_authors=("author", "nunique"),
    ).reset_index()

    total_stories = len(df)
    summary["story_share_pct"] = np.where(
        total_stories > 0,
        (summary["story_count"] / total_stories) * 100,
        0,
    )
    summary["avg_score"] = summary["avg_score"].round(2)
    summary["median_score"] = summary["median_score"].round(2)
    summary["avg_comments"] = summary["avg_comments"].round(2)
    summary["story_share_pct"] = summary["story_share_pct"].round(2)

    # Sort highest-volume categories first so the charting step has an intuitive order.
    summary = summary.sort_values(by=["story_count", "avg_score", "category"], ascending=[False, False, True])
    return summary


def build_overall_metrics(df):
    """Build a compact JSON-friendly report for the whole dataset."""
    return {
        "total_stories": int(len(df)),
        "unique_categories": int(df["category"].nunique()),
        "unique_authors": int(df["author"].nunique()),
        "average_score": round(float(df["score"].mean()), 2) if len(df) else 0.0,
        "average_comments": round(float(df["num_comments"].mean()), 2) if len(df) else 0.0,
        "max_score": int(df["score"].max()) if len(df) else 0,
        "min_score": int(df["score"].min()) if len(df) else 0,
        "top_category": str(df.groupby("category").size().idxmax()) if len(df) else "",
    }


def build_output_paths(input_csv_path):
    """Create date-stamped output paths that match the source file."""
    base_name = os.path.splitext(os.path.basename(input_csv_path))[0]
    suffix = base_name.replace("cleaned_trends_", "")
    summary_csv = os.path.join(DATA_DIR, f"analysis_summary_{suffix}.csv")
    summary_json = os.path.join(DATA_DIR, f"analysis_summary_{suffix}.json")
    return summary_csv, summary_json


def save_outputs(category_summary, overall_metrics, csv_path, json_path):
    """Write the summary tables and metrics to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)

    category_summary.to_csv(csv_path, index=False)

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "overall_metrics": overall_metrics,
        "category_summary": category_summary.to_dict(orient="records"),
    }
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)


def parse_args():
    """Parse optional command-line arguments."""
    parser = argparse.ArgumentParser(description="Analyze cleaned TrendPulse data with pandas and NumPy.")
    parser.add_argument("csv_path", nargs="?", help="Path to the cleaned trends CSV file.")
    parser.add_argument("--csv-output", help="Optional output path for the summary CSV.")
    parser.add_argument("--json-output", help="Optional output path for the summary JSON.")
    return parser.parse_args()


def main():
    args = parse_args()

    csv_path = args.csv_path or find_latest_cleaned_csv()
    if not csv_path:
        print("No cleaned CSV file found in the data folder.")
        return

    try:
        raw_df = load_data(csv_path)
    except (OSError, ValueError, pd.errors.EmptyDataError) as exc:
        print(f"Failed to load CSV data: {exc}")
        return

    cleaned_df = clean_dataframe(raw_df)
    category_summary = build_category_summary(cleaned_df)
    overall_metrics = build_overall_metrics(cleaned_df)

    summary_csv, summary_json = build_output_paths(csv_path)
    summary_csv = args.csv_output or summary_csv
    summary_json = args.json_output or summary_json

    save_outputs(category_summary, overall_metrics, summary_csv, summary_json)

    print(f"Analyzed {len(cleaned_df)} stories. Saved to {summary_csv} and {summary_json}")


if __name__ == "__main__":
    main()