"""
Filters raw scraped reviews down to ones actually worth hand-labeling.

Keeps only:
- 1-2 star reviews (far more likely to contain real complaints)
- reviews with more than 5 words (cuts out "good", "nice", "very good" junk)

Usage:
    python filter_reviews.py
"""

import json
import csv
import random

INPUT_JSON = "data/uc_reviews.json"
OUTPUT_JSON = "data/uc_reviews_filtered.json"
OUTPUT_CSV = "data/uc_reviews_filtered.csv"
SAMPLE_FOR_LABELING = "data/hand_label_sample.csv"
MIN_WORDS = 6
SAMPLE_SIZE = 30


def load_reviews():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def is_substantive(review):
    text = (review.get("text") or "").strip()
    rating = review.get("rating")
    if rating not in (1, 2):
        return False
    if len(text.split()) < MIN_WORDS:
        return False
    return True


def main():
    all_reviews = load_reviews()
    filtered = [r for r in all_reviews if is_substantive(r)]

    print(f"Started with {len(all_reviews)} reviews.")
    print(f"Kept {len(filtered)} substantive 1-2 star reviews (>= {MIN_WORDS} words).")

    if not filtered:
        print("No reviews passed the filter. Check MIN_WORDS or rating filter.")
        return

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=filtered[0].keys())
        writer.writeheader()
        writer.writerows(filtered)

    # Pull a random sample for hand-labeling, with an empty column for your tag
    sample_size = min(SAMPLE_SIZE, len(filtered))
    sample = random.sample(filtered, sample_size)

    with open(SAMPLE_FOR_LABELING, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["review_id", "rating", "text", "your_tag"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in sample:
            writer.writerow({
                "review_id": r.get("review_id"),
                "rating": r.get("rating"),
                "text": r.get("text"),
                "your_tag": ""  # fill this in yourself
            })

    print(f"Saved {len(filtered)} filtered reviews to {OUTPUT_JSON} / {OUTPUT_CSV}")
    print(f"Saved a random {sample_size}-review hand-labeling sheet to {SAMPLE_FOR_LABELING}")
    print("Open that file, fill in 'your_tag' for each row with your own short label, then send it back.")


if __name__ == "__main__":
    main()