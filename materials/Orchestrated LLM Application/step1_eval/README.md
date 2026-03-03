# step1_eval

## Intent

**"Add evaluation incrementally."** — The first step beyond the MVP.

Two additions over `minimal_mvp`:

1. **Step 1 — Claim Decomposition**: Extract structured components and generate targeted search queries in a separate LLM call.
2. **Pipeline Evaluation (B)**: Measure system accuracy against a small test set with known ground-truth labels.

---

## Diff from MVP

| Function | Change | Description |
| -------- | ------ | ----------- |
| `decompose_claim()` | **[NEW]** | Separate LLM call that decomposes a claim and generates 3 targeted search queries |
| `check_credibility()` | **[UPDATED]** | Now accepts `decomposition` and uses its targeted queries instead of a free-form prompt |
| `evaluate_pipeline()` | **[NEW]** | Runs test cases through the pipeline and measures label accuracy + score range |
| `run_single()` | **[NEW]** | Wrapper that chains decompose → check sequentially |

---

## Why Claim Decomposition matters (Step 1)

```text
Before (MVP): Tell LLM "search from supporting / opposing / fact-check angles" — strategy is opaque
After  (here): Decompose claim first, then pass explicit queries to the search step

Input: "COVID vaccines cause autism"
  ↓ decompose_claim()
{
  "subject": "COVID vaccines",
  "domain": "medical",
  "search_queries": [
    "COVID vaccine autism link studies supporting",        ← support angle
    "COVID vaccine autism debunked scientific evidence",   ← deny angle
    "COVID vaccine autism expert consensus WHO CDC"        ← expert angle
  ]
}
  ↓ check_credibility() searches with all 3 queries
```

**Effect**: Structurally reduces confirmation bias. Search strategy becomes traceable.

---

## Pipeline Evaluation (B) design

```python
TEST_CASES = [
    {"claim": "Earth is flat",            "expected": "Misinformation", "score_max": 10},
    {"claim": "Vaccines cause autism",    "expected": "Misinformation", "score_max": 15},
    {"claim": "Eiffel Tower is in Paris", "expected": "Likely True",    "score_min": 90},
    {"claim": "8 glasses of water/day",   "expected": "Contested",      "score": 20–70},
]
```

Metrics per test case:

- **Label match**: `predicted_label == expected_label`
- **Score range check**: score falls within the expected range
- "Contested" is the hardest case — can the LLM correctly withhold a strong verdict?

---

## Next steps

- **Step 2**: Source Scoring — assign individual reliability scores to each source
- **Step 3**: Contradiction Detection — extract source-vs-source contradictions structurally
- **Step 4**: Scoring Agent — aggregate outputs into a weighted composite score

---

## How to run

```bash
/c/Users/yuila/miniconda3/python.exe main.py
# Mode: [1] Single claim  [2] Evaluate pipeline
```
