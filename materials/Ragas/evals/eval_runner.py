"""
Phase 4 — 評価パイプラインのメインスクリプト

=== このスクリプトが行うこと ===
1. テストデータセット (testset.json) を読み込む
2. 各質問を Orchestrator Agent に投げて回答を得る
3. Agent のツール呼び出しから contexts（検索結果）を自動抽出する
4. カスタムメトリクス (metrics.py) で 6 種類の評価を実行する
5. 結果を JSON + サマリとして保存する

=== ARCHITECTURE.md の "Phase 4: Evaluation Data Flow" に対応 ===
  TestDataset → eval_runner.py → Agent → ChromaDB/OpenAI → Custom Metrics → Report

=== 実行方法 ===
  Docker 内:
    docker compose exec backend python /evals/eval_runner.py

  Docker 内（Agent 実行スキップ、既存データで評価のみ）:
    docker compose exec backend python /evals/eval_runner.py --skip-collect

  ローカル (Git Bash):
    cd /c/Users/yuila/Documents/FDE2ndBatchTraning/materials/Ragas
    /c/Users/yuila/miniconda3/python.exe evals/eval_runner.py --skip-collect
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# パスの設定. Docker とローカル両方で動くように工夫
# ---------------------------------------------------------------------------
EVALS_DIR    = Path(__file__).resolve().parent
PROJECT_ROOT = EVALS_DIR.parent
BACKEND_DIR  = Path("/app") if Path("/app/main.py").exists() else PROJECT_ROOT / "backend"
IN_DOCKER    = BACKEND_DIR == Path("/app")

TESTSET_PATH = Path("/evals/testset.json") if IN_DOCKER else EVALS_DIR / "testset.json"
RESULTS_DIR  = Path("/evals/results")      if IN_DOCKER else EVALS_DIR / "results"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(EVALS_DIR) not in sys.path:
    sys.path.insert(0, str(EVALS_DIR))

# ---------------------------------------------------------------------------
# imports (sys.path 設定後)
# ---------------------------------------------------------------------------
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from ai_agents.tools import _collection, _format_products, _embed
from ai_agents.orchestrator import INSTRUCTIONS
from metrics import evaluate_sample

for env_path in (BACKEND_DIR / ".env", PROJECT_ROOT / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break


# ===================================================================
# Step 1: テストデータセットの読み込み
# ===================================================================
def load_testset(path: Path = TESTSET_PATH) -> list[dict]:
    """
    testset.json を読み込む。

    期待するフォーマット:
    [
        {
            "query": "防水のランニングシューズはありますか？",
            "ground_truth": "Nike Pegasus Trail は防水で $120 です。",  ← GT あり評価用（省略可）
            "product_id": null                                          ← 省略可
        },
        ...
    ]
    """
    with open(path, "r", encoding="utf-8") as f:
        testset = json.load(f)

    print(f"[Step 1] Loaded {len(testset)} questions from {path.name}")
    return testset


# ===================================================================
# Step 2 & 3: Agent を実行して query / contexts / response を収集
# ===================================================================

# --- contexts 抽出のための仕組み ---
#
# 問題: run_orchestrator() は最終回答（文字列）しか返さない。
#        評価には「Agent が検索で取得したコンテキスト」も必要。
#
# 解決策: search_products ツールをラップして、呼ばれるたびに
#          検索結果を記録する。これで contexts を後から取り出せる。

# グローバルに検索結果を一時保存するリスト
_captured_contexts: list[str] = []


def _make_capturing_tools():
    """
    全ツールのラッパーを作る。
    各ツールの出力を _captured_contexts に記録しつつ、元のロジックを実行する。
    """
    @function_tool
    async def search_products(query: str, limit: int = 5) -> str:
        """Search for products using natural language.

        Args:
            query: Natural language search query (e.g. "organic skincare under $30").
            limit: Maximum number of results to return (1-15).
        """
        limit = max(1, min(15, limit))
        vector = await _embed(query)

        results = _collection().query(
            query_embeddings=[vector],
            n_results=limit,
            include=["metadatas"],
        )
        metadatas = results.get("metadatas", [[]])[0]
        formatted = _format_products(metadatas, limit)
        _captured_contexts.append(formatted)
        return formatted

    @function_tool
    def get_product(product_id: str) -> str:
        """Retrieve full details for a specific product by its ID.

        Args:
            product_id: The unique product identifier.
        """
        results = _collection().get(ids=[product_id], include=["metadatas"])
        metadatas = results.get("metadatas", [])
        if not metadatas:
            return f"Product {product_id} not found."

        m = metadatas[0]
        fields = [
            ("Product ID", product_id),
            ("Name", m.get("product_name")),
            ("Price", f"${m['final_price']:.2f}" if m.get("final_price") else None),
            ("Rating", m.get("rating")),
            ("Reviews", m.get("review_count")),
            ("Brand", m.get("brand")),
            ("Category", m.get("category_name")),
            ("Delivery", m.get("available_for_delivery")),
            ("Pickup", m.get("available_for_pickup")),
            ("Description", m.get("description")),
            ("Specifications", m.get("specifications")),
            ("Ingredients", m.get("ingredients")),
        ]
        output = "\n".join(f"{k}: {v}" for k, v in fields if v is not None)
        _captured_contexts.append(output)
        return output

    @function_tool
    def analyze_reviews(product_id: str) -> str:
        """Retrieve and return customer reviews for a product so you can analyze them.

        Returns the raw reviews text. Summarize positives, negatives, and overall
        quality in your response.

        Args:
            product_id: The unique product identifier.
        """
        results = _collection().get(ids=[product_id], include=["metadatas"])
        metadatas = results.get("metadatas", [])
        if not metadatas:
            return f"Product {product_id} not found."

        m = metadatas[0]
        reviews = m.get("customer_reviews")
        rating = m.get("rating")
        review_count = m.get("review_count")

        if not reviews:
            return f"No customer reviews available for product {product_id}."

        output = (
            f"Product: {m.get('product_name', product_id)}\n"
            f"Rating: {rating} ({review_count} reviews)\n\n"
            f"Customer Reviews:\n{reviews}"
        )
        _captured_contexts.append(output)
        return output

    @function_tool
    def recommend_alternatives(category_name: str, min_rating: float = 4.0, limit: int = 5) -> str:
        """Find alternative products in the same category with a minimum rating.

        Use this when a product has poor reviews and you want to suggest better options.

        Args:
            category_name: Product category to search within.
            min_rating: Minimum acceptable rating (default 4.0).
            limit: Number of alternatives to return (1-10).
        """
        limit = max(1, min(10, limit))
        try:
            results = _collection().get(
                where={
                    "$and": [
                        {"category_name": {"$eq": category_name}},
                        {"rating": {"$gte": min_rating}},
                    ]
                },
                include=["metadatas"],
                limit=limit,
            )
            metadatas = results.get("metadatas", [])
        except Exception:
            metadatas = []

        if not metadatas:
            return f"No alternatives found in '{category_name}' with rating >= {min_rating}."

        output = f"Top alternatives in '{category_name}' (rating >= {min_rating}):\n" + _format_products(metadatas, limit)
        _captured_contexts.append(output)
        return output

    return search_products, get_product, analyze_reviews, recommend_alternatives


async def run_single_eval(query: str, product_id: str | None = None) -> dict:
    """
    1 つの質問を Agent に投げて、評価に必要なデータを収集する。

    Returns:
        {
            "query": "...",
            "contexts": ["検索結果1", "検索結果2", ...],
            "response": "Agent の最終回答",
        }
    """
    global _captured_contexts
    _captured_contexts = []  # 前回の結果をクリア

    # contexts をキャプチャするツール付きの Agent を作成
    capturing_search, get_prod, analyze, recommend = _make_capturing_tools()

    eval_agent = Agent(
        name="Orchestrator-Eval",
        model="gpt-4o-mini",
        instructions=INSTRUCTIONS,
        tools=[capturing_search, get_prod, analyze, recommend],
    )

    # Agent を実行
    if product_id:
        user_input = f"[Context: product_id={product_id}]\n\n{query}"
    else:
        user_input = query

    result = await Runner.run(eval_agent, input=user_input)

    return {
        "query": query,
        "contexts": list(_captured_contexts),  # ツール呼び出しで記録された検索結果
        "response": result.final_output,
    }


async def collect_all_responses(testset: list[dict]) -> list[dict]:
    """
    テストセットの全質問を Agent に投げて、評価データを収集する。

    Agent は API 呼び出しを含むので、1 件ずつ逐次実行する。
    （並列にすると API レートリミットに引っかかるため）
    """
    collected = []
    total = len(testset)

    for i, item in enumerate(testset, 1):
        query = item["query"]
        product_id = item.get("product_id")
        print(f"[Step 2-3] ({i}/{total}) Processing: {query[:60]}...")

        try:
            result = await run_single_eval(query, product_id)
            if "ground_truth" in item and item["ground_truth"]:
                result["ground_truth"] = item["ground_truth"]
            collected.append(result)
        except Exception as e:
            print(f"  ERROR: {e}")
            collected.append({
                "query": query,
                "contexts": [],
                "response": f"ERROR: {e}",
                "error": True,
            })

        # API レートリミット対策: 1 件ごとに少し待つ
        if i < total:
            await asyncio.sleep(1)

    print(f"[Step 2-3] Collected {len(collected)} responses")
    return collected


# ===================================================================
# Step 4: カスタムメトリクスで評価を実行
# ===================================================================

async def run_custom_evaluation(collected: list[dict]) -> dict:
    """
    収集した全サンプルに対してカスタムメトリクスを実行する。

    Returns:
        {
            "per_sample": [
                {"query": "...", "faithfulness": {"score": ..., "details": ...}, ...},
                ...
            ],
            "aggregated": {
                "faithfulness": 0.85,
                "answer_relevancy": 0.91,
                ...
            }
        }
    """
    valid = [c for c in collected if not c.get("error")]
    total = len(valid)

    print(f"[Step 4] Evaluating {total} samples with 6 custom metrics...")

    per_sample = []

    for i, sample in enumerate(valid, 1):
        print(f"[Step 4] ({i}/{total}) Evaluating: {sample['query'][:50]}...")

        try:
            result = await evaluate_sample(
                query=sample["query"],
                contexts=sample.get("contexts", []),
                response=sample.get("response", ""),
                ground_truth=sample.get("ground_truth"),
            )
            result["query"] = sample["query"]
            per_sample.append(result)

            # 逐次出力: メトリクススコアのみ
            parts = []
            for m, label in [("faithfulness", "faith"), ("answer_relevancy", "ans_rel"),
                              ("context_relevance", "ctx_rel"), ("hallucination_detection", "halluc")]:
                s = result.get(m, {}).get("score") if isinstance(result.get(m), dict) else None
                parts.append(f"{label}={s:.2f}" if s is not None else f"{label}=N/A")
            print(f"  -> {', '.join(parts)}")
        except Exception as e:
            print(f"  ERROR evaluating: {e}")
            per_sample.append({
                "query": sample["query"],
                "error": str(e),
            })

        # API レートリミット対策
        if i < total:
            await asyncio.sleep(1)

    # --- 集計: 各メトリクスの平均スコア ---
    metric_names = [
        "faithfulness", "answer_relevancy", "context_relevance",
        "context_precision", "context_recall", "hallucination_detection",
    ]

    aggregated = {}
    for metric in metric_names:
        scores = [
            s[metric]["score"]
            for s in per_sample
            if not s.get("error") and s.get(metric, {}).get("score") is not None
        ]
        if scores:
            aggregated[metric] = round(sum(scores) / len(scores), 4)
        else:
            aggregated[metric] = None

    return {
        "per_sample": per_sample,
        "aggregated": aggregated,
    }


# ===================================================================
# Step 5: 結果の保存と表示
# ===================================================================
def save_results(eval_result: dict, collected: list[dict], output_dir: Path = RESULTS_DIR):
    """
    評価結果を JSON ファイルとして保存し、サマリを表示する。
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    result_path = output_dir / f"eval_{timestamp}.json"

    output = {
        "timestamp": timestamp,
        "num_questions": len(collected),
        "scores_summary": eval_result["aggregated"],
        "per_question": eval_result["per_sample"],
    }

    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    # サマリ表示 (ASCII 文字のみ — Windows Git Bash 対応)
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    for metric, score in eval_result["aggregated"].items():
        if score is not None:
            bar = "#" * int(score * 20) + "." * (20 - int(score * 20))
            print(f"  {metric:<25s} [{bar}] {score:.3f}")
        else:
            print(f"  {metric:<25s} [     N/A (no GT)      ]  ---")
    print("=" * 60)
    print(f"\nSaved to: {result_path}")

    return output


# ===================================================================
# メイン実行
# ===================================================================
async def main():
    print("=" * 60)
    print("Phase 4 -- RAG Evaluation Pipeline (Custom Metrics)")
    print("=" * 60)

    # --skip-collect フラグ: Agent 実行をスキップして既存データで評価のみ行う
    # 使い方: python eval_runner.py --skip-collect
    # Agent 実行は API コスト ($) がかかるので、評価のデバッグ時に便利
    skip_collect = "--skip-collect" in sys.argv

    # --testset <path>: 使用する testset ファイルを指定（デフォルト: testset.json）
    testset_override = None
    for i, arg in enumerate(sys.argv):
        if arg == "--testset" and i + 1 < len(sys.argv):
            testset_override = sys.argv[i + 1]

    if testset_override:
        testset_path = Path(testset_override)
        if not testset_path.is_absolute():
            testset_path = (Path("/evals") if IN_DOCKER else EVALS_DIR) / testset_path
    else:
        testset_path = TESTSET_PATH

    intermediate_path = RESULTS_DIR / "collected_latest.json"

    if skip_collect and intermediate_path.exists():
        print("[Skip] Loading previously collected data...")
        with open(intermediate_path, "r", encoding="utf-8") as f:
            collected = json.load(f)
        print(f"[Skip] Loaded {len(collected)} responses from {intermediate_path}")
    else:
        # Step 1: テストデータ読み込み
        testset = load_testset(testset_path)

        # Step 2-3: Agent 実行 & データ収集
        collected = await collect_all_responses(testset)

        # 収集データを中間ファイルとして保存（デバッグ用）
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(intermediate_path, "w", encoding="utf-8") as f:
            json.dump(collected, f, indent=2, ensure_ascii=False)
        print(f"[Debug] Saved intermediate data to {intermediate_path}")

    # Step 4: カスタムメトリクスで評価
    eval_result = await run_custom_evaluation(collected)

    # Step 5: 結果保存
    save_results(eval_result, collected)


if __name__ == "__main__":
    asyncio.run(main())
