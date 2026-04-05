# TrendPulse

TrendPulse is a 4-part Python data pipeline that fetches trending stories from the Hacker News API, cleans the collected data, performs a small analysis step with pandas and NumPy, and generates a visualization.

Repository: https://github.com/iamyoganathan/trendpulse-yoganathan

## Project Files

- `task1_data_collection.py` - fetches Hacker News top stories, assigns categories, and saves JSON output
- `task2_data_processing.py` - loads the JSON file, cleans the records, and saves `data/trends_clean.csv`
- `task3_analysis.py` - analyzes the cleaned CSV and saves `data/trends_analysed.csv`
- `task4_visualization.py` - creates three charts and a dashboard from the analysed CSV

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

If you are using the project virtual environment, you can run:

```powershell
d:/Mini-Pro/.venv/Scripts/python.exe task1_data_collection.py
d:/Mini-Pro/.venv/Scripts/python.exe task2_data_processing.py
d:/Mini-Pro/.venv/Scripts/python.exe task3_analysis.py
d:/Mini-Pro/.venv/Scripts/python.exe task4_visualization.py
```

## Output Files

The pipeline writes its results into the `data/` folder:

- `data/trends_YYYYMMDD.json`
- `data/trends_clean.csv`
- `data/trends_analysed.csv`
- `outputs/chart1_top_stories.png`
- `outputs/chart2_categories.png`
- `outputs/chart3_scatter.png`
- `outputs/dashboard.png`

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
- Task 4 uses the analysed CSV produced by Task 3.

## Submission

For the assignment, push the files to a public GitHub repository and share the direct blob links for each task script.

## Direct Task Links

- Task 1: https://github.com/iamyoganathan/trendpulse-yoganathan/blob/main/task1_data_collection.py
- Task 2: https://github.com/iamyoganathan/trendpulse-yoganathan/blob/main/task2_data_processing.py
- Task 3: https://github.com/iamyoganathan/trendpulse-yoganathan/blob/main/task3_analysis.py
- Task 4: https://github.com/iamyoganathan/trendpulse-yoganathan/blob/main/task4_visualization.py
