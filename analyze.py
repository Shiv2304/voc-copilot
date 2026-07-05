

import json
import sys
import os
import csv
from google import genai

SYSTEM_PROMPT = """You are a product analyst turning raw customer reviews into a
structured Voice of Customer report. Follow these rules strictly:

1. Only create a theme if it is supported by at least 5 reviews, or at least
   8% of the sample if the sample is small. Anything below that goes in a
   "long_tail" list instead of "themes".
2. Every theme must cite the review_ids that support it. Never invent a claim
   that isn't backed by at least 2 real reviews from the input.
3. Each theme needs: theme_name, count, percent_of_sample, example_quotes
   (2-3, each with review_id), sentiment_note, root_cause, recommendation,
   confidence (high/medium/low), severity (critical/high/medium/low).
4. severity is INDEPENDENT of count. A low-count theme involving safety,
   legal risk, fraud, or financial harm to customers (e.g. theft, assault,
   warranty fraud, deceptive billing) must be marked "critical" or "high"
   regardless of how many reviews mention it. A high-count theme that is
   just an annoyance (e.g. slow chat response) should not automatically be
   "critical" just because the count is large.
5. root_cause must name the specific, mechanical reason the problem happens
   — not a vague category. Bad: "poor scheduling." Good: "OTP validity
   window doesn't match early-morning booking slots, so codes expire before
   the customer can use them." If the reviews don't give enough detail to
   infer a specific mechanism, say so explicitly rather than guessing.
6. recommendation must follow from the root_cause, not just restate the
   complaint. Do not merge unrelated complaints just because both are
   negative.
7. Output ONLY valid JSON. No preamble, no markdown fences, nothing else.

Output schema:
{
  "sample_size": <int>,
  "themes": [
    {
      "theme_name": "...",
      "count": <int>,
      "percent_of_sample": <float>,
      "example_quotes": [{"review_id": "...", "quote": "..."}],
      "sentiment_note": "...",
      "root_cause": "...",
      "recommendation": "...",
      "confidence": "high|medium|low",
      "severity": "critical|high|medium|low"
    }
  ],
  "long_tail": ["one-line description of below-threshold complaints"]
}
"""


def load_reviews(path):
    if path.lower().endswith(".csv"):
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = []
            for r in reader:
                rows.append({
                    "review_id": r.get("review_id"),
                    "rating": r.get("rating"),
                    "text": r.get("text"),
                })
            return rows
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_reviews_for_prompt(reviews):
    lines = []
    for r in reviews:
        rid = r.get("review_id", "unknown")
        rating = r.get("rating", "?")
        text = r.get("text", "")
        lines.append(f"[{rid}] (rating: {rating}) {text}")
    return "\n".join(lines)


def analyze(reviews):
    client = genai.Client()  # reads GEMINI_API_KEY from env
    reviews_block = format_reviews_for_prompt(reviews)

    user_prompt = f"""{SYSTEM_PROMPT}

Here are {len(reviews)} customer reviews. Analyze them per the rules above.

{reviews_block}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config={
            "max_output_tokens": 16000,
            "thinking_config": {"thinking_budget": 0},
        },
    )

    raw_text = response.text
    # strip stray fences just in case
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        debug_path = "output/_raw_response_debug.txt"
        os.makedirs("output", exist_ok=True)
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(raw_text)
        print(f"JSON parse failed: {e}")
        print(f"Raw response saved to {debug_path} for inspection.")
        print("This usually means the response got cut off (too many reviews in one call)")
        print("or the model added extra text. Try filtering to fewer reviews per batch.")
        raise


def main():
    if len(sys.argv) != 3:
        print("Usage: python analyze.py <input_reviews.json_or_csv> <output_themes.json>")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]
    reviews = load_reviews(input_path)
    result = analyze(reviews)
    result["sample_size"] = len(reviews)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Analyzed {len(reviews)} reviews -> {output_path}")
    print(f"Found {len(result.get('themes', []))} themes above threshold.")


if __name__ == "__main__":
    main()