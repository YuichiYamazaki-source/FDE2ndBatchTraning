import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# ============================================================
# [NEW] Step 1: Claim Decomposer
#   MVPとの差分: クレームを構造化してから検索クエリを生成する
# ============================================================

DECOMPOSE_PROMPT = """You are a claim analysis expert.
Decompose the given claim into structured components for systematic fact-checking.
Be precise and objective. Do not judge credibility at this stage.
"""

def decompose_claim(claim: str) -> dict:
    """[NEW] クレームを分解して検索クエリを生成する"""
    response = client.responses.create(
        model="gpt-4o",
        instructions=DECOMPOSE_PROMPT,
        input=f"""Decompose this claim: "{claim}"

Output a JSON object with exactly this structure:
{{
  "subject": "main entity being discussed",
  "predicate": "action or relationship being claimed",
  "object": "what is claimed about the subject",
  "domain": "<one of: medical | political | scientific | economic | social | historical | other>",
  "timeframe": "when this claim refers to (or 'ongoing')",
  "search_queries": [
    "query 1 - angle that would SUPPORT this claim",
    "query 2 - angle that would CONTRADICT or DEBUNK this claim",
    "query 3 - scientific or expert consensus angle"
  ]
}}

Output ONLY the JSON, nothing else."""
    )

    text = response.output_text
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        # フォールバック: 元のクレームをそのまま検索クエリにする
        return {"domain": "other", "search_queries": [claim]}


# ============================================================
# Credibility Checker
#   [UPDATED] decomposition を受け取り、生成済みクエリで検索する
#   MVPとの差分: input に domain と search_queries を追加
# ============================================================

SYSTEM_PROMPT = """You are a news credibility checker.

Given a claim and pre-generated search queries, you will:
1. Search using ALL provided queries (supporting AND opposing views)
2. Compare what different sources say
3. Identify any contradictions
4. Assign a credibility score based on source consensus and evidence quality

Always use every provided query before concluding.
"""

def check_credibility(claim: str, decomposition: dict) -> dict:
    """[UPDATED] decompositionから得た targeted queries で評価する"""
    queries   = decomposition.get("search_queries", [claim])
    domain    = decomposition.get("domain", "general")

    query_list = "\n".join(f"{i+1}. {q}" for i, q in enumerate(queries))

    response = client.responses.create(
        model="gpt-4o",
        tools=[{"type": "web_search_preview"}],
        instructions=SYSTEM_PROMPT,
        input=f"""Verify this claim: "{claim}"
Domain: {domain}

Use these targeted search queries (search ALL of them):
{query_list}

After searching, output a JSON object with exactly this structure:
{{
  "score": <integer 0-100>,
  "label": "<one of: Likely True | Mostly Supported | Contested | Likely False | Misinformation>",
  "sources": [
    {{"outlet": "...", "stance": "supports|denies|neutral", "key_point": "..."}}
  ],
  "contradictions": ["..."],
  "explanation": "2-3 sentence summary"
}}

Output ONLY the JSON, nothing else."""
    )

    text = response.output_text
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return {"raw": text}


# ============================================================
# [NEW] B: Pipeline Evaluation
#   既知の正解ラベルを持つテストケースでパイプラインの精度を測る
# ============================================================

# ラベルの信頼度順序 (スコアが近ければ許容する場合に使う)
LABEL_ORDER = ["Misinformation", "Likely False", "Contested", "Mostly Supported", "Likely True"]

TEST_CASES = [
    {
        "claim": "The Earth is flat",
        "expected_label": "Misinformation",
        "score_max": 10,
    },
    {
        "claim": "COVID-19 vaccines cause autism",
        "expected_label": "Misinformation",
        "score_max": 15,
    },
    {
        "claim": "The Eiffel Tower is located in Paris, France",
        "expected_label": "Likely True",
        "score_min": 90,
    },
    {
        "claim": "Drinking 8 glasses of water per day is scientifically required",
        "expected_label": "Contested",
        "score_min": 20,
        "score_max": 70,
    },
]


def _score_in_range(score: int, tc: dict) -> bool:
    if "score_min" in tc and score < tc["score_min"]:
        return False
    if "score_max" in tc and score > tc["score_max"]:
        return False
    return True


def evaluate_pipeline():
    """[NEW] テストケースをパイプラインに通して精度を測定する"""
    results = []

    print("\n" + "=" * 60)
    print("PIPELINE EVALUATION")
    print("=" * 60)

    for i, tc in enumerate(TEST_CASES):
        claim = tc["claim"]
        print(f"\n[{i+1}/{len(TEST_CASES)}] {claim}")

        # Step 1: Decompose
        decomp = decompose_claim(claim)
        print(f"  Domain  : {decomp.get('domain')}")

        # Step 2: Credibility check with targeted queries
        result = check_credibility(claim, decomp)

        predicted_label = result.get("label", "N/A")
        predicted_score = result.get("score", -1)
        label_match     = predicted_label == tc["expected_label"]
        score_ok        = _score_in_range(predicted_score, tc)
        passed          = label_match and score_ok

        results.append({
            "claim":           claim,
            "expected_label":  tc["expected_label"],
            "predicted_label": predicted_label,
            "predicted_score": predicted_score,
            "label_match":     label_match,
            "score_ok":        score_ok,
            "passed":          passed,
        })

        label_str = "OK" if label_match else "NG"
        score_str = "OK" if score_ok   else "NG"
        print(f"  Expected : {tc['expected_label']}")
        print(f"  Predicted: {predicted_label} (score: {predicted_score})")
        print(f"  Label={label_str}  Score={score_str}  => {'PASS' if passed else 'FAIL'}")

    # --- Summary ---
    n_passed = sum(1 for r in results if r["passed"])
    n_label  = sum(1 for r in results if r["label_match"])
    n_score  = sum(1 for r in results if r["score_ok"])
    total    = len(results)

    print("\n" + "=" * 60)
    print(f"EVALUATION SUMMARY")
    print(f"  Overall  : {n_passed}/{total} passed")
    print(f"  Label    : {n_label}/{total} correct")
    print(f"  Score    : {n_score}/{total} in expected range")
    print("=" * 60)
    for r in results:
        icon = "✓" if r["passed"] else "✗"
        print(f"  {icon} [{r['predicted_score']:3d}] {r['predicted_label']:<20s} | {r['claim'][:50]}")

    return results


# ============================================================
# Display helper (MVPから移植 + domain 行を追加)
# ============================================================

def display_result(claim: str, result: dict, decomp: dict | None = None):
    print("\n" + "=" * 60)
    print(f"CLAIM : {claim}")
    if decomp:
        print(f"DOMAIN: {decomp.get('domain', 'N/A')}  |  "
              f"SUBJECT: {decomp.get('subject', 'N/A')}")
    print("=" * 60)

    if "raw" in result:
        print(result["raw"])
        return

    score  = result.get("score", 0)
    label  = result.get("label", "N/A")
    filled = score // 5
    bar    = "#" * filled + "-" * (20 - filled)
    print(f"\nSCORE : {score}/100  [{bar}]")
    print(f"LABEL : {label}\n")

    sources = result.get("sources", [])
    if sources:
        print("SOURCES:")
        icons = {"supports": "[+]", "denies": "[-]", "neutral": "[o]"}
        for s in sources:
            icon = icons.get(s.get("stance"), "[?]")
            print(f"  {icon} [{s.get('stance'):8}]  {s.get('outlet')}")
            print(f"              -> {s.get('key_point')}")

    contradictions = result.get("contradictions", [])
    if contradictions:
        print("\nCONTRADICTIONS:")
        for c in contradictions:
            print(f"  !! {c}")

    print(f"\nSUMMARY:\n  {result.get('explanation', '')}")
    print("=" * 60)


# ============================================================
# Single claim runner
# ============================================================

def run_single(claim: str):
    print(f'\nChecking: "{claim}"\n')

    # [NEW] Step 1: Decompose
    print("Step 1: Decomposing claim...")
    decomp = decompose_claim(claim)
    print(f"  Domain  : {decomp.get('domain')}")
    print(f"  Subject : {decomp.get('subject')}")
    print(f"  Queries : {len(decomp.get('search_queries', []))} generated")
    for q in decomp.get("search_queries", []):
        print(f"    - {q}")

    # Step 2: Search & evaluate with targeted queries
    print("\nStep 2: Searching & evaluating...")
    result = check_credibility(claim, decomp)

    display_result(claim, result, decomp)


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    print("Mode: [1] Single claim  [2] Evaluate pipeline")
    mode = input("Choose (1/2): ").strip()

    if mode == "2":
        evaluate_pipeline()
    else:
        claim = input("Enter claim to verify: ").strip()
        if claim:
            run_single(claim)
        else:
            print("No claim entered.")
