# Eval Rubric — Voice of Customer Copilot

This defines what "good" output looks like before any code is written.
If the model's output doesn't meet these bars, the pipeline is wrong,
not the rubric.

## Bad output (reject this)
- Vague summaries with no numbers: "Users are unhappy with onboarding."
- Insights with no source: "Users want faster refunds." (says who? how many?)
- Themes that are really just re-stated ratings: "Many users gave 1 star."
- Recommendations with no reasoning: "Improve customer support."
- Merged unrelated complaints into one theme because they're both "negative."

## Good output (this is the bar)
- Quantified: "12 out of 50 reviews mention onboarding confusion (24%)."
- Specific: "5 users specifically said they could not complete the first
  setup step during professional verification."
- Sourced: every theme links to at least 2 real review IDs/snippets it's
  based on, so a PM can go check the raw data themselves.
- Actionable: recommendation ties to a plausible root cause, not just
  "fix it" — e.g. "Reschedule flow likely needs a clearer cancellation
  fee disclosure before confirm, not just support-side messaging."
- Correctly separates signal from noise: a 1-off angry review is not a
  theme. A theme needs a minimum support threshold (see below).

## Minimum support threshold
- A cluster only becomes a "theme" if it has >= 5 reviews or >= 8% of
  the sample, whichever is lower for small datasets.
- Below that, it's listed under "long tail / watch list," not as a
  roadmap recommendation.

## Required output fields per theme
1. `theme_name` — short, specific (not "negative feedback")
2. `count` and `percent_of_sample`
3. `example_quotes` — 2-3 real excerpts, each tagged with review_id
4. `sentiment_note` — is this rising, steady, or a known long-standing issue
5. `root_cause` — the specific, mechanical reason the problem happens, not
   a vague category (e.g. not "poor scheduling" but "OTP validity window
   doesn't match early-morning booking slots, so codes expire before the
   customer can use them")
6. `recommendation` — one sentence, tied to the root cause above
7. `confidence` — high/medium/low, based on sample size and consistency
8. `severity` — critical/high/medium/low, assigned INDEPENDENTLY of count.
   A low-count theme involving safety, legal risk, fraud, or financial harm
   must be marked critical or high regardless of how many reviews mention
   it. A high-count theme that's just an annoyance should not automatically
   be "critical" just because the count is large.

## How to test the pipeline (the actual eval)
1. Hand-label 30 reviews yourself first, before running the model.
   Write down what themes you see and how many reviews support each.
2. Run the pipeline on those same 30 reviews.
3. Compare: did the model find the same themes? Same counts (+/- 1-2)?
   Did it hallucinate a theme with no real support?
4. If mismatch, this tells you where the prompt needs tightening —
   which is a stronger portfolio story than "it worked first try."

## The friend test (do not skip this)
Give the tool to 2 people who actually do PM/founder work. Ask:
- "Would you trust this to help you prioritize, or would you still
  go read the raw reviews yourself?"
- "What's missing that would make you actually use this weekly?"
Write down their answers verbatim (with permission) — this becomes
your strongest interview talking point, stronger than the tool itself.

## Known limitations (stated deliberately, not oversights)
- Cohort tagging (free vs paying users) is not implemented: Play Store
  reviews don't include subscription status, so this data isn't available
  from the source. Would require a different data source entirely.
- Trend velocity (e.g. "up 50% from last week") is not implemented: this
  needs repeated scrapes over time, which requires a scheduled job and
  hosted infrastructure — deliberately out of scope for this version.