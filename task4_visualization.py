import os

import matplotlib.pyplot as plt
import pandas as pd


DATA_FILE = os.path.join("data", "trends_analysed.csv")
OUTPUT_DIR = "outputs"
CHART1_FILE = os.path.join(OUTPUT_DIR, "chart1_top_stories.png")
CHART2_FILE = os.path.join(OUTPUT_DIR, "chart2_categories.png")
CHART3_FILE = os.path.join(OUTPUT_DIR, "chart3_scatter.png")
DASHBOARD_FILE = os.path.join(OUTPUT_DIR, "dashboard.png")


def load_data(csv_path):
    """Load the analysed CSV from Task 3."""
    return pd.read_csv(csv_path)


def ensure_outputs_folder():
    """Create the outputs folder if it does not already exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def shorten_title(title, max_length=50):
    """Trim long story titles so the charts stay readable."""
    text = str(title).strip()
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."


def style_axes(axis):
    """Apply a simple, consistent grid style to an axis."""
    axis.grid(axis="x", linestyle="--", alpha=0.25)


def save_figure(fig, output_path):
    """Save a figure before any display call."""
    fig.savefig(output_path, dpi=200, bbox_inches="tight")


def create_chart1(frame, output_path):
    """Create a horizontal bar chart for the top 10 stories by score."""
    top_stories = frame.nlargest(10, "score").copy()
    top_stories = top_stories.sort_values("score", ascending=True)
    top_stories["short_title"] = top_stories["title"].apply(shorten_title)

    fig, axis = plt.subplots(figsize=(12, 7))
    axis.barh(top_stories["short_title"], top_stories["score"], color="#2D7DD2")
    axis.set_title("Top 10 Stories by Score")
    axis.set_xlabel("Score")
    axis.set_ylabel("Story Title")
    axis.invert_yaxis()
    style_axes(axis)

    save_figure(fig, output_path)
    plt.close(fig)


def create_chart2(frame, output_path):
    """Create a category bar chart with a different colour for each bar."""
    category_counts = frame["category"].value_counts().reindex(
        ["technology", "worldnews", "sports", "science", "entertainment"]
    )
    category_counts = category_counts.dropna()

    colours = ["#2458A6", "#2D7DD2", "#3AB795", "#F4A259", "#E76F51"]

    fig, axis = plt.subplots(figsize=(10, 6))
    axis.bar(category_counts.index, category_counts.values, color=colours[: len(category_counts)])
    axis.set_title("Stories per Category")
    axis.set_xlabel("Category")
    axis.set_ylabel("Number of Stories")
    axis.tick_params(axis="x", rotation=20)
    style_axes(axis)

    save_figure(fig, output_path)
    plt.close(fig)


def create_chart3(frame, output_path):
    """Create a scatter plot showing score versus comments."""
    fig, axis = plt.subplots(figsize=(10, 6))

    popular = frame[frame["is_popular"] == True]  # noqa: E712
    not_popular = frame[frame["is_popular"] == False]  # noqa: E712

    axis.scatter(
        not_popular["score"],
        not_popular["num_comments"],
        alpha=0.7,
        label="Non-popular",
        color="#E76F51",
    )
    axis.scatter(
        popular["score"],
        popular["num_comments"],
        alpha=0.8,
        label="Popular",
        color="#2D7DD2",
    )
    axis.set_title("Score vs Comments")
    axis.set_xlabel("Score")
    axis.set_ylabel("Number of Comments")
    axis.legend()
    style_axes(axis)

    save_figure(fig, output_path)
    plt.close(fig)


def create_dashboard(frame, output_path):
    """Combine all three charts into one dashboard figure."""
    top_stories = frame.nlargest(10, "score").copy()
    top_stories = top_stories.sort_values("score", ascending=True)
    top_stories["short_title"] = top_stories["title"].apply(shorten_title)

    category_counts = frame["category"].value_counts().reindex(
        ["technology", "worldnews", "sports", "science", "entertainment"]
    ).dropna()

    popular = frame[frame["is_popular"] == True]  # noqa: E712
    not_popular = frame[frame["is_popular"] == False]  # noqa: E712

    fig, axes = plt.subplots(1, 3, figsize=(22, 7), constrained_layout=True)
    fig.suptitle("TrendPulse Dashboard", fontsize=22, fontweight="bold")

    axes[0].barh(top_stories["short_title"], top_stories["score"], color="#2D7DD2")
    axes[0].set_title("Top 10 Stories by Score")
    axes[0].set_xlabel("Score")
    axes[0].set_ylabel("Story Title")
    axes[0].invert_yaxis()
    style_axes(axes[0])

    category_colours = ["#2458A6", "#2D7DD2", "#3AB795", "#F4A259", "#E76F51"]
    axes[1].bar(category_counts.index, category_counts.values, color=category_colours[: len(category_counts)])
    axes[1].set_title("Stories per Category")
    axes[1].set_xlabel("Category")
    axes[1].set_ylabel("Number of Stories")
    axes[1].tick_params(axis="x", rotation=20)
    style_axes(axes[1])

    axes[2].scatter(
        not_popular["score"],
        not_popular["num_comments"],
        alpha=0.7,
        label="Non-popular",
        color="#E76F51",
    )
    axes[2].scatter(
        popular["score"],
        popular["num_comments"],
        alpha=0.8,
        label="Popular",
        color="#2D7DD2",
    )
    axes[2].set_title("Score vs Comments")
    axes[2].set_xlabel("Score")
    axes[2].set_ylabel("Number of Comments")
    axes[2].legend()
    style_axes(axes[2])

    save_figure(fig, output_path)
    plt.close(fig)


def main():
    if not os.path.exists(DATA_FILE):
        print(f"Missing input file: {DATA_FILE}")
        return

    ensure_outputs_folder()
    data = load_data(DATA_FILE)

    # Normalize the columns so plotting stays predictable.
    data["title"] = data["title"].astype("string").str.strip()
    data["category"] = data["category"].astype("string").str.strip().str.lower()
    data["score"] = pd.to_numeric(data["score"], errors="coerce").fillna(0)
    data["num_comments"] = pd.to_numeric(data["num_comments"], errors="coerce").fillna(0)
    data["is_popular"] = data["is_popular"].astype(str).str.lower().isin(["true", "1", "yes"])

    create_chart1(data, CHART1_FILE)
    create_chart2(data, CHART2_FILE)
    create_chart3(data, CHART3_FILE)
    create_dashboard(data, DASHBOARD_FILE)

    print(f"Saved {CHART1_FILE}")
    print(f"Saved {CHART2_FILE}")
    print(f"Saved {CHART3_FILE}")
    print(f"Saved {DASHBOARD_FILE}")


if __name__ == "__main__":
    main()