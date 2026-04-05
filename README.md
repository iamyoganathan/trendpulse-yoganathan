# TrendPulse

TrendPulse is a 4-part Python data pipeline that fetches trending stories from the Hacker News API, cleans the collected data, performs a small analysis step with pandas and NumPy, and generates a visualization.

## Project Files

- `task1_data_collection.py` - fetches Hacker News top stories, assigns categories, and saves JSON output
- `task2_data_processing.py` - loads the JSON file, cleans the records, and saves a CSV file
- `task3_analysis.py` - analyzes the cleaned CSV and writes category summary outputs
- `task4_visualization.py` - creates a chart dashboard from the analysis summary

## Requirements

- Python 3.13+
- Packages:
  - `requests`
  - `pandas`
  - `numpy`
  - `matplotlib`

If you are using the included virtual environment, activate it first.

## How to Run

Run the scripts in order:

```powershell
python task1_data_collection.py
python task2_data_processing.py
python task3_analysis.py
python task4_visualization.py
```

## Output Files

The pipeline writes its results into the `data/` folder:

- `data/trends_YYYYMMDD.json`
- `data/cleaned_trends_YYYYMMDD.csv`
- `data/analysis_summary_YYYYMMDD.csv`
- `data/analysis_summary_YYYYMMDD.json`
- `data/trendpulse_visualization_YYYYMMDD.png`

## What Task 1 Does

- Fetches the first 500 story IDs from Hacker News top stories
- Fetches story details using the required `User-Agent` header
- Groups stories into these categories:
  - technology
  - worldnews
  - sports
  - science
  - entertainment
- Collects the required fields:
  - `post_id`
  - `title`
  - `category`
  - `score`
  - `num_comments`
  - `author`
  - `collected_at`

## Notes

- The scripts are designed to keep running even if individual API requests fail.
- Task 1 and Task 2 are tolerant of missing or malformed records.
- Task 4 uses the analysis summary produced by Task 3.

## Submission

For the assignment, push the files to a public GitHub repository and share the direct blob links for each task script.
