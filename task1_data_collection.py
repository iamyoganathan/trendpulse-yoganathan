import json
import os
import time
import warnings
from datetime import datetime

import requests
from requests.exceptions import RequestException
from urllib3.exceptions import InsecureRequestWarning


TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL_TEMPLATE = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
HEADERS = {"User-Agent": "TrendPulse/1.0"}
REQUEST_TIMEOUT = 8

# Keep the category order fixed so assignment is consistent when titles match multiple groups.
CATEGORY_KEYWORDS = {
    "technology": ["AI", "software", "tech", "code", "computer", "data", "cloud", "API", "GPU", "LLM"],
    "worldnews": ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports": ["NFL", "NBA", "FIFA", "sport", "game", "team", "player", "league", "championship"],
    "science": ["research", "study", "space", "physics", "biology", "discovery", "NASA", "genome"],
    "entertainment": ["movie", "film", "music", "Netflix", "game", "book", "show", "award", "streaming"],
}


def build_session():
    """Create a requests session with the required header and a safe fallback."""
    session = requests.Session()
    session.headers.update(HEADERS)
    session.verify = False
    return session


def fetch_top_story_ids(session, limit=500):
    """Fetch the top story IDs and return the first `limit` IDs."""
    try:
        response = session.get(TOP_STORIES_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        ids = response.json()
    except RequestException as exc:
        print(f"Failed to fetch top story IDs: {exc}")
        return []

    if not isinstance(ids, list):
        print("Unexpected response format for top story IDs.")
        return []

    return ids[:limit]


def fetch_story(session, story_id):
    """Fetch one story by ID. Returns a story dict or None when unavailable."""
    url = ITEM_URL_TEMPLATE.format(id=story_id)

    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        story = response.json()
    except RequestException as exc:
        print(f"Failed to fetch story {story_id}: {exc}")
        return None

    if not isinstance(story, dict):
        print(f"Story {story_id} returned unexpected data and was skipped.")
        return None

    # We only process items with titles, because category assignment is title-based.
    if not story.get("title"):
        return None

    return story


def fetch_story_cached(session, story_id, cache):
    """Fetch a story once and reuse it across category passes."""
    if story_id not in cache:
        cache[story_id] = fetch_story(session, story_id)
    return cache[story_id]


def title_matches_category(title, keywords):
    """Check if title contains any keyword (case-insensitive)."""
    title_lower = title.lower()
    return any(keyword.lower() in title_lower for keyword in keywords)


def build_record(story, category):
    """Extract required fields and return a normalized output record."""
    return {
        "post_id": story.get("id"),
        "title": story.get("title", ""),
        "category": category,
        "score": story.get("score", 0),
        "num_comments": story.get("descendants", 0),
        "author": story.get("by", ""),
        "collected_at": datetime.now().isoformat(timespec="seconds"),
    }


def collect_trending_stories(max_per_category=25):
    """Fetch stories and collect up to max_per_category records for each category."""
    session = build_session()
    top_ids = fetch_top_story_ids(session, limit=500)
    if not top_ids:
        return []

    results = []
    story_cache = {}
    category_names = list(CATEGORY_KEYWORDS.keys())

    for index, category in enumerate(category_names):
        keywords = CATEGORY_KEYWORDS[category]
        category_count = 0
        category_seen_ids = set()

        for story_id in top_ids:
            if category_count >= max_per_category:
                break

            if story_id in category_seen_ids:
                continue

            story = fetch_story_cached(session, story_id, story_cache)
            if story is None:
                continue

            title = story.get("title", "")
            if title_matches_category(title, keywords):
                results.append(build_record(story, category))
                category_seen_ids.add(story_id)
                category_count += 1

        # Stop early once every category has enough stories.
        if len(results) >= max_per_category * len(category_names):
            break

        # Sleep only between category loops (as required), not after the last category.
        if index < len(category_names) - 1:
            time.sleep(2)

    return results


def save_to_json(records):
    """Create data folder if needed and save records to date-stamped JSON file."""
    os.makedirs("data", exist_ok=True)
    date_stamp = datetime.now().strftime("%Y%m%d")
    output_path = os.path.join("data", f"trends_{date_stamp}.json")

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

    return output_path


def main():
    warnings.simplefilter("ignore", InsecureRequestWarning)

    records = collect_trending_stories(max_per_category=25)
    output_file = save_to_json(records)

    print(f"Collected {len(records)} stories. Saved to {output_file}")


if __name__ == "__main__":
    main()
