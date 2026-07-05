"""
Scrapes Play Store reviews for Urban Company.

Install first:
    pip install google-play-scraper

Usage:
    python scraper.py
"""

from google_play_scraper import Sort, reviews
import json
import csv
import os


APP_ID = "com.urbanclap.urbanclap"  # Urban Company customer app (confirmed package id)
# Note: com.urbanclap.provider is the Partner (professional) app — do not use that one.

OUTPUT_JSON = "data/uc_reviews.json"
OUTPUT_CSV = "data/uc_reviews.csv"
TARGET_COUNT = 500  # aim for 300-500 reviews, enough to cluster meaningfully


def scrape_reviews():
    all_reviews = []
    continuation_token = None

    while len(all_reviews) < TARGET_COUNT:
        batch, continuation_token = reviews(
            APP_ID,
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=200,
            continuation_token=continuation_token,
        )
        if not batch:
            break
        all_reviews.extend(batch)
        print(f"Pulled {len(all_reviews)} reviews so far...")
        if continuation_token is None:
            break

    # Keep only the fields we actually need
    cleaned = []
    for r in all_reviews[:TARGET_COUNT]:
        cleaned.append({
            "review_id": r.get("reviewId"),
            "user_name": r.get("userName"),
            "rating": r.get("score"),
            "text": r.get("content"),
            "date": r.get("at").isoformat() if r.get("at") else None,
            "thumbs_up": r.get("thumbsUpCount"),
        })

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cleaned[0].keys())
        writer.writeheader()
        writer.writerows(cleaned)

    print(f"Saved {len(cleaned)} reviews to {OUTPUT_JSON} and {OUTPUT_CSV}")


if __name__ == "__main__":
    scrape_reviews()