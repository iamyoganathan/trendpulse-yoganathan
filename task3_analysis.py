import os

import numpy as np
import pandas as pd


DATA_DIR = "data"
INPUT_FILE = os.path.join(DATA_DIR, "trends_clean.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "trends_analysed.csv")


def load_data(csv_path):
    """Load the cleaned CSV from Task 2 into a DataFrame."""
    return pd.read_csv(csv_path)


def print_overview(frame):
    """Print the basic exploration details required by the assignment."""
    print(f"Loaded data: {frame.shape}")
    print()
    print("First 5 rows:")
    print(frame.head())
    print()
    print(f"Average score   : {frame['score'].mean():.2f}")
    print(f"Average comments: {frame['num_comments'].mean():.2f}")


def print_numpy_stats(frame):
    """Use NumPy to calculate the requested statistics."""
    scores = frame["score"].to_numpy()
    comments = frame["num_comments"].to_numpy()

    most_story_category = frame["category"].value_counts().idxmax()
    most_story_count = int(frame["category"].value_counts().max())

    top_comment_index = int(np.argmax(comments))
    top_comment_title = frame.iloc[top_comment_index]["title"]
    top_comment_count = int(comments[top_comment_index])

    print("--- NumPy Stats ---")
    print(f"Mean score   : {np.mean(scores):.2f}")
    print(f"Median score : {np.median(scores):.2f}")
    print(f"Std deviation: {np.std(scores):.2f}")
    print(f"Max score    : {np.max(scores):.0f}")
    print(f"Min score    : {np.min(scores):.0f}")
    print()
    print(f"Most stories in: {most_story_category} ({most_story_count} stories)")
    print()
    print(f'Most commented story: "{top_comment_title}"  — {top_comment_count} comments')


def add_columns(frame):
    """Add the engagement and is_popular columns."""
    enriched = frame.copy()
    average_score = enriched["score"].mean()

    # Engagement shows how much discussion a story gets per upvote.
    enriched["engagement"] = enriched["num_comments"] / (enriched["score"] + 1)

    # Popular stories are those scoring above the overall average.
    enriched["is_popular"] = enriched["score"] > average_score

    return enriched


def save_result(frame, csv_path):
    """Save the updated DataFrame to the Task 3 output CSV."""
    os.makedirs(DATA_DIR, exist_ok=True)
    frame.to_csv(csv_path, index=False)


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Missing input file: {INPUT_FILE}")
        return

    data = load_data(INPUT_FILE)

    # Normalize the important fields so the statistics and comparisons are reliable.
    data["title"] = data["title"].astype("string").str.strip()
    data["category"] = data["category"].astype("string").str.strip().str.lower()
    data["score"] = pd.to_numeric(data["score"], errors="coerce").fillna(0).astype(int)
    data["num_comments"] = pd.to_numeric(data["num_comments"], errors="coerce").fillna(0).astype(int)

    print_overview(data)
    print()
    print_numpy_stats(data)

    analysed = add_columns(data)
    save_result(analysed, OUTPUT_FILE)

    print()
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()