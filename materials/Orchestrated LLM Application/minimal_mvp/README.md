# minimal_mvp

## Intent

**"Make something that works first."** — A minimal single-agent implementation.

The goal is to understand the core problem (how to evaluate claim credibility)
with a single file and a single LLM call, before pursuing the ideal architecture.

---

## What it does

```text
Input: claim string
  ↓
One LLM call (gpt-4o + web_search_preview)
  ↓
Output: score / label / sources / contradictions / explanation
```

The prompt instructs the LLM to search from three angles
(supporting / contradicting / fact-check), but the actual search strategy
is entirely left to the LLM.

---

## Limitations (why the next step is needed)

| Problem | Symptom |
| ------- | ------- |
| Search strategy is a black box | Cannot track what was searched or from what angle |
| All sources have equal weight | Peer-reviewed papers treated the same as gossip sites |
| Contradiction detection is shallow | Tends to end with just "contradiction found" |
| Score reasoning is opaque | Cannot explain why a particular score was given |
| No re-search on weak evidence | Pipeline ends after a single pass |

→ These problems are resolved incrementally starting from `step1_eval/`.

---

## How to run

```bash
# Set OPENAI_API_KEY in .env first
/c/Users/yuila/miniconda3/python.exe main.py
```
