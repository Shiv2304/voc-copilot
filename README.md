# Voice of Customer Copilot — Urban Company

Turns raw customer feedback into structured, sourced, quantified product roadmap recommendations.

**Live dashboard:** https://shiv2304.github.io/voc-copilot/dashboard/

## Why this project

In a real PM job, feedback comes from everywhere: app reviews, support tickets, sales calls, WhatsApp screenshots from founders. This project answers the actual day-one workflow: turning messy feedback into a prioritized, defensible view of what to build next.

The differentiator isn't the AI clustering. It's the eval design. See eval_rubric.md. Every insight is quantified, sourced back to a real review, and tied to a plausible root cause, not a vague summary. Every theme also carries a severity rating judged independently of how many reviews mention it, so a rare but serious issue (like a safety complaint) doesn't get buried under a high-volume but low-stakes one (like slow chat support).

## What's in this repo

```
voc-copilot/
├── scraper.py              pulls Urban Company Play Store reviews
├── filter_reviews.py       cuts low-signal reviews (e.g. "good", "nice") before analysis
├── analyze.py              clusters reviews into themes with citations, root cause, severity
├── eval_rubric.md          defines good vs bad output before any code was written
├── case_study.md           full writeup: process, validation, friend feedback, iteration
├── requirements.txt
├── data/                   scraped and filtered review data
├── output/                 pipeline output (themes, quotes, recommendations)
└── dashboard/
    └── index.html          live two-pane demo dashboard
```

## How to run this

### 1. Get real data

```
pip install -r requirements.txt
python scraper.py
```

This needs a real internet connection since it hits play.google.com.

### 2. Filter out low-signal reviews

```
python filter_reviews.py
```

Roughly half of raw app store reviews are one-word noise ("good", "nice") that can't inform any theme. This step keeps only substantive 1-2 star reviews and also produces a random sample for hand-labeling.

### 3. Hand-label a sample before trusting any AI output

Open the hand-labeling sample this script produces and write your own tag for what each review is actually about, independent of any model. This is the step that lets you catch a pipeline that's hallucinating patterns instead of finding real ones.

### 4. Run the analysis pipeline

This project uses Google's Gemini API (free tier, no card required) rather than a paid API, since that was a real constraint during development. Get a free key at https://aistudio.google.com.

```
set GEMINI_API_KEY=your_key_here
python analyze.py data/uc_reviews_filtered.csv output/themes.json
```

### 5. Compare the pipeline's output against your hand-labels

Check whether the same themes and counts show up. If they don't match, that tells you where the prompt needs tightening, which is a stronger project story than assuming the first output is correct.

### 6. Open the dashboard

dashboard/index.html is fully self-contained, no server or API key needed to view it, since the analyzed data is embedded directly in the file. Open it in any browser, or visit the live link above.

## What's deliberately not built, and why

- **Cohort tagging** (free vs paying users): not possible from this data source. Play Store reviews don't include subscription status.
- **Trend tracking over time** (e.g. "up 50% from last week"): would need repeated scrapes on a schedule and a hosted backend. This is real infrastructure work, not a prompt change, and was deliberately left out of this version rather than half-built.

Both are documented here on purpose, not left out by accident. See case_study.md for the full reasoning and the friend feedback that shaped these decisions.

## The step that actually mattered most

Two people who do real PM or founder work looked at this and gave direct feedback, including a specific flaw in the first version (frequency was masking severity). That feedback changed the pipeline's prompt design. The full iteration story, what changed and why, is in case_study.md.
