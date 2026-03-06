"""
QA / Hallucination / Validation テスト

最新の評価結果 (evals/results/eval_*.json) を読み込み、
各メトリクスが閾値を満たしているかを pytest でチェックする。

実行:
  ローカル:
    cd materials/Ragas && /c/Users/yuila/miniconda3/python.exe -m pytest evals/test_quality.py -v -s
  Docker 内:
    docker compose exec backend python -m pytest /evals/test_quality.py -v -s
"""

import json
from pathlib import Path

import pytest

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def _load_latest_results() -> dict:
    """最新の eval_*.json を読み込む。"""
    files = sorted(RESULTS_DIR.glob("eval_*.json"))
    if not files:
        pytest.skip("No evaluation results found in evals/results/")
    data = json.loads(files[-1].read_text(encoding="utf-8"))
    print(f"\n{'=' * 60}")
    print(f"  Evaluation File : {files[-1].name}")
    print(f"  Timestamp       : {data.get('timestamp', 'N/A')}")
    print(f"  Total Questions : {data.get('num_questions', 'N/A')}")
    print(f"{'=' * 60}")
    return data


@pytest.fixture(scope="module")
def results():
    return _load_latest_results()


@pytest.fixture(scope="module")
def scores(results):
    return results["scores_summary"]


@pytest.fixture(scope="module")
def per_question(results):
    return results["per_question"]


# =========================================================================
# Helper: per-question スコアを集計して表示
# =========================================================================

def _print_per_question_scores(per_question: list, metric: str, threshold: float, higher_is_better: bool = True):
    """各質問のスコアを表示し、pass/fail を判定する。"""
    passed = 0
    failed = 0
    skipped = 0
    total = len(per_question)

    print(f"\n  --- Per-Question Breakdown: {metric} ---")
    print(f"  {'#':<4} {'Score':<8} {'Result':<6} Query")
    print(f"  {'─' * 70}")

    for i, q in enumerate(per_question):
        query_short = q.get("query", "")[:50]
        metric_data = q.get(metric, {})
        score = metric_data.get("score") if isinstance(metric_data, dict) else None

        if score is None:
            status = "SKIP"
            skipped += 1
            print(f"  {i+1:<4} {'N/A':<8} {status:<6} {query_short}")
        else:
            if higher_is_better:
                ok = score >= threshold
            else:
                ok = score <= threshold
            status = "PASS" if ok else "FAIL"
            if ok:
                passed += 1
            else:
                failed += 1
            print(f"  {i+1:<4} {score:<8.3f} {status:<6} {query_short}")

    evaluated = passed + failed
    pass_rate = (passed / evaluated * 100) if evaluated > 0 else 0

    print(f"  {'─' * 70}")
    op = ">=" if higher_is_better else "<="
    print(f"  Threshold : {metric} {op} {threshold}")
    print(f"  Result    : {passed}/{evaluated} passed ({pass_rate:.0f}%), {skipped} skipped")
    print()


# =========================================================================
# QA Test: 回答品質
# =========================================================================

class TestQA:
    def test_faithfulness_above_threshold(self, scores, per_question):
        """faithfulness 平均が 0.5 以上"""
        print(f"\n  [QA Test] Faithfulness (= response is grounded in contexts)")
        print(f"  Average Score : {scores['faithfulness']:.4f}" if scores["faithfulness"] is not None else "  Average Score : N/A")
        print(f"  Threshold     : >= 0.5")

        _print_per_question_scores(per_question, "faithfulness", 0.5, higher_is_better=True)

        assert scores["faithfulness"] is not None
        assert scores["faithfulness"] >= 0.5, (
            f"faithfulness {scores['faithfulness']:.3f} < 0.5"
        )

    def test_answer_relevancy_above_threshold(self, scores, per_question):
        """answer_relevancy 平均が 0.5 以上"""
        print(f"\n  [QA Test] Answer Relevancy (= response addresses the query)")
        print(f"  Average Score : {scores['answer_relevancy']:.4f}" if scores["answer_relevancy"] is not None else "  Average Score : N/A")
        print(f"  Threshold     : >= 0.5")

        _print_per_question_scores(per_question, "answer_relevancy", 0.5, higher_is_better=True)

        assert scores["answer_relevancy"] is not None
        assert scores["answer_relevancy"] >= 0.5, (
            f"answer_relevancy {scores['answer_relevancy']:.3f} < 0.5"
        )


# =========================================================================
# Hallucination Test: 幻覚検出
# =========================================================================

class TestHallucination:
    def test_hallucination_below_threshold(self, scores, per_question):
        """hallucination 平均が 0.5 以下"""
        print(f"\n  [Hallucination Test] Hallucination Detection (= lower is better)")
        print(f"  Average Score : {scores['hallucination_detection']:.4f}" if scores["hallucination_detection"] is not None else "  Average Score : N/A")
        print(f"  Threshold     : <= 0.5")

        _print_per_question_scores(per_question, "hallucination_detection", 0.5, higher_is_better=False)

        assert scores["hallucination_detection"] is not None
        assert scores["hallucination_detection"] <= 0.5, (
            f"hallucination {scores['hallucination_detection']:.3f} > 0.5"
        )

    def test_no_complete_hallucination(self, per_question):
        """contexts ありなのに faithfulness=0.0 のサンプルがない"""
        print(f"\n  [Hallucination Test] Complete Hallucination Check")
        print(f"  (= no sample should have faithfulness=0.0 with actual claims)")

        flagged = []
        for i, q in enumerate(per_question):
            faith = q.get("faithfulness", {})
            score = faith.get("score") if isinstance(faith, dict) else None
            if score == 0.0:
                details = faith.get("details", {})
                total = details.get("total_claims", 0)
                if total > 0:
                    flagged.append((i, total, q.get("query", "")[:50]))

        if flagged:
            print(f"\n  FLAGGED ({len(flagged)} samples with complete hallucination):")
            for idx, claims, query in flagged:
                print(f"    Sample {idx+1}: faithfulness=0.0, {claims} claims -- {query}")
        else:
            print(f"  Result    : 0 complete hallucinations found in {len(per_question)} samples -- PASS")

        for idx, claims, query in flagged:
            pytest.fail(
                f"Sample {idx+1}: faithfulness=0.0 with {claims} claims "
                f"(complete hallucination) -- query: {query}"
            )


# =========================================================================
# Validation Test: Context 品質 + Recall
# =========================================================================

class TestValidation:
    def test_context_relevance_above_threshold(self, scores, per_question):
        """context_relevance 平均が 0.4 以上"""
        print(f"\n  [Validation Test] Context Relevance (= retrieved docs are relevant)")
        print(f"  Average Score : {scores['context_relevance']:.4f}" if scores["context_relevance"] is not None else "  Average Score : N/A")
        print(f"  Threshold     : >= 0.4")

        _print_per_question_scores(per_question, "context_relevance", 0.4, higher_is_better=True)

        assert scores["context_relevance"] is not None
        assert scores["context_relevance"] >= 0.4, (
            f"context_relevance {scores['context_relevance']:.3f} < 0.4"
        )

    def test_context_recall_with_gt(self, scores, per_question):
        """GT が反映されたら context_recall が数値スコアを返す"""
        score = scores.get("context_recall")

        print(f"\n  [Validation Test] Context Recall (= contexts cover ground truth)")
        if score is not None:
            print(f"  Average Score : {score:.4f}")
        else:
            print(f"  Average Score : N/A (ground truth not available in evaluation data)")
        print(f"  Threshold     : >= 0.4")

        if score is not None:
            _print_per_question_scores(per_question, "context_recall", 0.4, higher_is_better=True)

        if score is None:
            pytest.skip("context_recall is N/A (no GT in evaluated data)")
        assert score >= 0.4, (
            f"context_recall {score:.3f} < 0.4"
        )
