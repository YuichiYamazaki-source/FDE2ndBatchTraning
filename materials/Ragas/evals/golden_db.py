"""
Golden Database 生成スクリプト

collected_latest.json（Agent の実行結果）を読み込み、
gpt-4o-mini で各クエリの ground truth を自動生成する。
生成後 golden_db.json に保存 → ユーザーが確認・修正 → 確定版とする。

実行:
  Docker 内:
    docker compose exec backend python /evals/golden_db.py
  ローカル:
    cd materials/Ragas && /c/Users/yuila/miniconda3/python.exe evals/golden_db.py
"""

import asyncio
import json
import sys
from pathlib import Path

# --- パス設定 ---
EVALS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = EVALS_DIR.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(EVALS_DIR))

from dotenv import load_dotenv

PROJECT_ROOT = EVALS_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")

from metrics import _llm_json, JUDGE_MODEL

COLLECTED_PATH = EVALS_DIR / "results" / "collected_latest.json"
GOLDEN_DB_PATH = EVALS_DIR / "golden_db.json"


async def generate_ground_truth(sample: dict) -> dict:
    """1 サンプルの ground truth を生成する。"""
    query = sample["query"]
    contexts = sample.get("contexts", [])
    response = sample.get("response", "")

    combined_ctx = "\n".join(contexts) if contexts else "(no search results)"

    result = await _llm_json(
        system_prompt=(
            "You are a ground truth generator for RAG evaluation.\n"
            "Given a user query, the search results (contexts), and the agent's response,\n"
            "generate an ideal ground truth answer.\n\n"
            "Rules:\n"
            "- Base your answer ONLY on information in the contexts\n"
            "- Include key facts: product names, prices, ratings, categories\n"
            "- Keep it concise (2-4 sentences)\n"
            "- If contexts are empty, base it on the agent's response\n\n"
            "Also extract:\n"
            "- category: the product category relevant to the query\n"
            "- price_range: the price range mentioned or implied\n\n"
            "Return JSON:\n"
            '{"ground_truth": "...", "category": "...", "price_range": "..."}'
        ),
        user_prompt=(
            f"Query: {query}\n\n"
            f"Contexts:\n{combined_ctx}\n\n"
            f"Agent response:\n{response}"
        ),
    )

    return {
        "query": query,
        "ground_truth": result.get("ground_truth", ""),
        "category": result.get("category", ""),
        "price_range": result.get("price_range", ""),
        "notes": "",
    }


async def main():
    if not COLLECTED_PATH.exists():
        print(f"ERROR: {COLLECTED_PATH} not found.")
        print("Run eval_runner.py first to collect agent responses.")
        sys.exit(1)

    collected = json.loads(COLLECTED_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(collected)} samples from collected_latest.json")
    print(f"Using model: {JUDGE_MODEL}")
    print()

    golden_db = []
    for i, sample in enumerate(collected):
        print(f"  [{i+1}/{len(collected)}] {sample['query'][:60]}...")
        entry = await generate_ground_truth(sample)
        golden_db.append(entry)

    GOLDEN_DB_PATH.write_text(
        json.dumps(golden_db, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print()
    print(f"Saved {len(golden_db)} entries to {GOLDEN_DB_PATH}")
    print()
    print("Next steps:")
    print("  1. Open golden_db.json and review/edit each ground_truth")
    print("  2. Run: python /evals/golden_db.py --apply  (to update testset.json)")


if __name__ == "__main__":
    if "--apply" in sys.argv:
        # golden_db.json → testset.json に統合
        if not GOLDEN_DB_PATH.exists():
            print("ERROR: golden_db.json not found. Generate it first.")
            sys.exit(1)

        golden = json.loads(GOLDEN_DB_PATH.read_text(encoding="utf-8"))
        testset_path = EVALS_DIR / "testset.json"
        testset = json.loads(testset_path.read_text(encoding="utf-8"))

        gt_map = {entry["query"]: entry["ground_truth"] for entry in golden}

        updated = 0
        for item in testset:
            gt = gt_map.get(item["query"])
            if gt:
                item["ground_truth"] = gt
                updated += 1

        testset_path.write_text(
            json.dumps(testset, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Updated {updated}/{len(testset)} entries in testset.json")
    else:
        asyncio.run(main())
