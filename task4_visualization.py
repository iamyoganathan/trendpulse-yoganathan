import argparse
import os

import matplotlib.pyplot as plt
import pandas as pd


DATA_DIR = "data"


def find_latest_summary_csv(data_dir=DATA_DIR):
    """Return the newest analysis summary CSV file in the data folder."""
    if not os.path.isdir(data_dir):
        return None

    candidates = []
    for name in os.listdir(data_dir):
        if name.startswith("analysis_summary_") and name.endswith(".csv"):
            candidates.append(os.path.join(data_dir, name))

    if not candidates:
        return None

    return max(candidates, key=os.path.getmtime)


def load_summary(csv_path):
    """Load the analysis summary into a DataFrame."""
    df = pd.read_csv(csv_path)

    required_columns = {
        "category",
        "story_count",
        "avg_score",
        "median_score",
        "max_score",
        "avg_comments",
        "total_comments",
        "unique_authors",
        "story_share_pct",
    }
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    return df


def create_visualization(df, output_path):
    """Build a compact dashboard with the key category metrics."""
    os.makedirs(DATA_DIR, exist_ok=True)

    frame = df.copy()
    frame = frame.sort_values(by=["story_count", "avg_score", "category"], ascending=[False, False, True])

    categories = frame["category"].tolist()
    colors = ["#2458A6", "#2D7DD2", "#3AB795", "#F4A259", "#E76F51"]

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), constrained_layout=True)
    fig.suptitle("TrendPulse: What is Trending Right Now", fontsize=20, fontweight="bold")

    # Story count chart.
    axes[0].bar(categories, frame["story_count"], color=colors[: len(categories)])
    axes[0].set_title("Stories per Category")
    axes[0].set_ylabel("Story Count")
    axes[0].tick_params(axis="x", rotation=25)

    # Average score chart.
    axes[1].bar(categories, frame["avg_score"], color=colors[: len(categories)])
    axes[1].set_title("Average Score")
    axes[1].set_ylabel("Average Score")
    axes[1].tick_params(axis="x", rotation=25)

    # Share of total stories chart.
    axes[2].pie(
        frame["story_share_pct"],
        labels=categories,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors[: len(categories)],
        textprops={"fontsize": 10},
    )
    axes[2].set_title("Share of Collected Stories")

    fig.patch.set_facecolor("white")
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def parse_args():
    """Parse optional command-line arguments."""
    parser = argparse.ArgumentParser(description="Visualize TrendPulse analysis results.")
    parser.add_argument("csv_path", nargs="?", help="Path to the analysis summary CSV file.")
    parser.add_argument("--output", help="Optional output PNG path.")
    return parser.parse_args()


def main():
    args = parse_args()

    csv_path = args.csv_path or find_latest_summary_csv()
    if not csv_path:
        print("No analysis summary CSV file found in the data folder.")
        return

    try:
        summary_df = load_summary(csv_path)
    except (OSError, ValueError, pd.errors.EmptyDataError) as exc:
        print(f"Failed to load analysis summary: {exc}")
        return

    output_path = args.output
    if not output_path:
        base_name = os.path.splitext(os.path.basename(csv_path))[0]
        suffix = base_name.replace("analysis_summary_", "")
        output_path = os.path.join(DATA_DIR, f"trendpulse_visualization_{suffix}.png")

    create_visualization(summary_df, output_path)

    print(f"Saved visualization to {output_path}")


if __name__ == "__main__":
    main()