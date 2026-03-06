"""
Custom RAG Evaluation Metrics — OpenAI API のみで実装

=== 概要 ===
全メトリクスの本質は「LLM-as-Judge」— LLM に評価させるパターン。

=== 6 メトリクス ===
1. Faithfulness       — 回答が contexts に裏付けられているか
2. Answer Relevancy   — 回答が質問に対して適切か
3. Context Relevance  — 取得した contexts が質問に関連してるか
4. Context Precision  — 関連 contexts が上位にランクされてるか
5. Context Recall     — GT の情報が contexts に含まれてるか (GT 必須)
6. Hallucination      — contexts にない情報を生成していないか

=== 使い方 ===
    from metrics import evaluate_sample

    result = await evaluate_sample(
        query="office chair under $200",
        contexts=["- [123] Chair A  $50  ⭐4.5", ...],
        response="Here are some chairs...",
        ground_truth=None,  # GT なしなら None
    )
    # result["faithfulness"]["score"] → 0.85
    # result["faithfulness"]["details"]["verdicts"] → [{claim, verdict, reason}, ...]

=== API コスト (15 サンプル、GT なし) ===
    gpt-4o-mini: 75 calls ≈ $0.06
    text-embedding-3-small: 15 calls ≈ $0.001
"""

import asyncio
import json
import math
import os
from openai import AsyncOpenAI


# =========================================================================
# OpenAI クライアント（シングルトン）
# =========================================================================
# 毎回 AsyncOpenAI() を作ると HTTP コネクションが無駄になる。
# モジュールレベルで 1 つだけ作り、全メトリクスで共有する。

_client: AsyncOpenAI | None = None

JUDGE_MODEL = "gpt-4o-mini"       # LLM 判定用（安くて速い）
EMBED_MODEL = "text-embedding-3-small"  # embedding 用


def _get_client() -> AsyncOpenAI:
    """AsyncOpenAI クライアントを取得（初回のみ生成）"""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _client


# =========================================================================
# ヘルパー関数
# =========================================================================

async def _llm_json(system_prompt: str, user_prompt: str, max_retries: int = 2) -> dict:
    """
    gpt-4o-mini を JSON mode で呼び出す。

    なぜ JSON mode を使うか:
    - response_format={"type": "json_object"} を指定すると、
      LLM は必ず有効な JSON を返す
    - これで「LLM の出力をパースできない」問題を回避

    Args:
        system_prompt: システムプロンプト（JSON 形式を指示）
        user_prompt:   評価対象のコンテンツ
        max_retries:   パース失敗時のリトライ回数

    Returns:
        パース済みの dict
    """
    client = _get_client()

    for attempt in range(max_retries + 1):
        try:
            resp = await client.chat.completions.create(
                model=JUDGE_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,  # 決定的な判定のため
            )
            content = resp.choices[0].message.content
            return json.loads(content)
        except (json.JSONDecodeError, KeyError) as e:
            if attempt == max_retries:
                raise ValueError(
                    f"Failed to get valid JSON after {max_retries + 1} attempts: {e}"
                )
    return {}


async def _get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    テキストのリストを 1 回の API コールでまとめて embedding 化。

    なぜバッチ化するか:
    - 1 テキストずつ呼ぶと API コール数が増えてレイテンシが上がる
    - バッチなら N テキストを 1 回のコールで処理できる
    """
    client = _get_client()
    resp = await client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )
    return [d.embedding for d in resp.data]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    2 つのベクトルのコサイン類似度を計算。

    コサイン類似度 = (A・B) / (|A| × |B|)
    - 1.0 = 完全に同じ方向（意味が近い）
    - 0.0 = 直交（無関係）
    - -1.0 = 正反対

    numpy を使わず pure Python で実装（依存を減らすため）。
    """
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# =========================================================================
# Metric 1: Faithfulness（忠実性）
# =========================================================================
#
# 「回答は検索結果（contexts）に基づいているか？」を測る。
#
# アルゴリズム:
#   Step 1: 回答を個々の「claim（主張）」に分解する
#           例: "Chair A は $50 で評価 4.5" → ["Chair A は $50", "Chair A の評価は 4.5"]
#   Step 2: 各 claim が contexts に裏付けられるか LLM に判定させる
#   Step 3: スコア = (裏付けられた claim 数) / (全 claim 数)
#
# なぜ 2 ステップに分けるか:
#   - 1 回の LLM コールで「分解 + 判定」をやると、出力が長くなりすぎて
#     max_tokens に引っかかる
#   - 分けることで各ステップの出力が短くなり、安定する

async def faithfulness(query: str, contexts: list[str], response: str) -> dict:
    """
    Faithfulness（忠実性）スコアを計算。

    Returns:
        {
            "score": 0.85,
            "details": {
                "total_claims": 10,
                "supported_claims": 8,
                "unsupported_claims": 2,
                "verdicts": [{"claim": "...", "verdict": "supported/unsupported", "reason": "..."}, ...]
            }
        }
    """
    if not contexts or not response:
        return {"score": 0.0, "details": {"reason": "empty contexts or response"}}

    combined_context = "\n\n".join(contexts)

    # --- Step 1: 回答から claim（主張）を抽出 ---
    claims_result = await _llm_json(
        system_prompt=(
            "You are a claim extraction assistant.\n"
            "Extract all factual claims from the given response.\n"
            "A claim is a single, atomic factual statement that can be verified.\n"
            "Do NOT include opinions, questions, or subjective statements.\n"
            "Keep each claim SHORT (one fact per claim).\n\n"
            'Return JSON: {"claims": ["claim1", "claim2", ...]}\n'
            'If no verifiable claims, return {"claims": []}'
        ),
        user_prompt=f"Response:\n{response}",
    )

    claims = claims_result.get("claims", [])
    if not claims:
        return {
            "score": 1.0,
            "details": {"reason": "no verifiable claims found", "claims": []},
        }

    # --- Step 2: 各 claim を contexts と照合 ---
    verify_result = await _llm_json(
        system_prompt=(
            "You are a claim verification assistant.\n"
            "For each claim, determine if it is supported by the given context.\n"
            '"supported" = the context contains information that confirms the claim.\n'
            '"unsupported" = the context does NOT contain information to confirm it.\n\n'
            "Return JSON:\n"
            '{"verdicts": [\n'
            '  {"claim": "...", "verdict": "supported", "reason": "brief reason"},\n'
            '  {"claim": "...", "verdict": "unsupported", "reason": "brief reason"}\n'
            "]}"
        ),
        user_prompt=(
            f"Context:\n{combined_context}\n\n"
            f"Claims to verify:\n{json.dumps(claims, ensure_ascii=False)}"
        ),
    )

    verdicts = verify_result.get("verdicts", [])
    supported = sum(1 for v in verdicts if v.get("verdict") == "supported")
    total = len(claims)
    score = supported / total if total > 0 else 0.0

    return {
        "score": round(score, 4),
        "details": {
            "total_claims": total,
            "supported_claims": supported,
            "unsupported_claims": total - supported,
            "verdicts": verdicts,
        },
    }


# =========================================================================
# Metric 2: Answer Relevancy（回答の関連性）
# =========================================================================
#
# 「回答は質問に対して適切か？」を測る。
#
# アルゴリズム:
#   Step 1: 回答から「この回答が答えになるような質問」を N 個生成（逆質問）
#   Step 2: 元の質問と各逆質問の embedding を取得
#   Step 3: コサイン類似度の平均 = スコア
#
# 直感的な理解:
#   - 良い回答 → 逆質問が元の質問に近くなる → スコア高い
#   - 的外れな回答 → 逆質問が元の質問と違う → スコア低い
#   - 例: 質問「椅子のおすすめは？」→ 回答が椅子について → 逆質問「おすすめの椅子は？」→ 類似度高い

async def answer_relevancy(
    query: str, contexts: list[str], response: str, n_questions: int = 3
) -> dict:
    """
    Answer Relevancy スコアを計算。

    Returns:
        {
            "score": 0.91,
            "details": {
                "generated_questions": ["Q1", "Q2", "Q3"],
                "similarities": [0.92, 0.90, 0.91],
                "mean_similarity": 0.91
            }
        }
    """
    if not response:
        return {"score": 0.0, "details": {"reason": "empty response"}}

    # --- Step 1: 逆質問を生成 ---
    gen_result = await _llm_json(
        system_prompt=(
            f"You are a question generation assistant.\n"
            f"Given a response text, generate exactly {n_questions} questions "
            f"that this response could be answering.\n"
            f"The questions should be diverse but all directly answerable "
            f"by the given response.\n\n"
            f"IMPORTANT: Preserve all identifiers (product IDs, model numbers, "
            f"brand names) from the response in your generated questions. "
            f"For example, if the response mentions 'Product 430528189', "
            f"include that ID in the question.\n\n"
            f'Return JSON: {{"questions": ["question1", "question2", ...]}}'
        ),
        user_prompt=f"Response:\n{response}",
    )

    questions = gen_result.get("questions", [])
    if not questions:
        return {"score": 0.0, "details": {"reason": "failed to generate reverse questions"}}

    # --- Step 2: embedding をバッチ取得（1 API コール） ---
    all_texts = [query] + questions
    embeddings = await _get_embeddings(all_texts)

    query_emb = embeddings[0]
    question_embs = embeddings[1:]

    # --- Step 3: コサイン類似度の平均 ---
    similarities = [_cosine_similarity(query_emb, q_emb) for q_emb in question_embs]
    score = sum(similarities) / len(similarities) if similarities else 0.0

    return {
        "score": round(score, 4),
        "details": {
            "generated_questions": questions,
            "similarities": [round(s, 4) for s in similarities],
            "mean_similarity": round(score, 4),
        },
    }


# =========================================================================
# Metric 3: Context Relevance（コンテキストの関連性）
# =========================================================================
#
# 「検索で取得した contexts は、質問に関連しているか？」を測る。
#
# アルゴリズム:
#   - 各 context について「この質問に答えるのに役立つか？」を LLM に判定させる
#   - スコア = (関連する context 数) / (全 context 数)
#
# なぜこれが重要か:
#   - 検索結果にゴミが多いと、LLM が混乱して悪い回答を生成する
#   - このメトリクスが低い → 検索（embedding / ChromaDB）の改善が必要

async def context_relevance(query: str, contexts: list[str], response: str) -> dict:
    """
    Context Relevance スコアを計算。

    Returns:
        {
            "score": 0.80,
            "details": {
                "total_contexts": 5,
                "relevant_contexts": 4,
                "judgments": [{"context_index": 1, "verdict": "relevant", "reason": "..."}, ...]
            }
        }
    """
    if not contexts:
        return {"score": 0.0, "details": {"reason": "no contexts provided"}}

    numbered = "\n\n".join(
        f"[Context {i + 1}]:\n{ctx}" for i, ctx in enumerate(contexts)
    )

    result = await _llm_json(
        system_prompt=(
            "You are a relevance judgment assistant.\n"
            "For each context chunk, determine if it is relevant to answering the given query.\n"
            '"relevant" = contains information that could help answer the query.\n'
            '"irrelevant" = has no useful information for the query.\n\n'
            "Return JSON:\n"
            '{"judgments": [\n'
            '  {"context_index": 1, "verdict": "relevant", "reason": "brief reason"},\n'
            '  {"context_index": 2, "verdict": "irrelevant", "reason": "brief reason"}\n'
            "]}"
        ),
        user_prompt=f"Query: {query}\n\n{numbered}",
    )

    judgments = result.get("judgments", [])
    relevant_count = sum(1 for j in judgments if j.get("verdict") == "relevant")
    total = len(contexts)
    score = relevant_count / total if total > 0 else 0.0

    return {
        "score": round(score, 4),
        "details": {
            "total_contexts": total,
            "relevant_contexts": relevant_count,
            "judgments": judgments,
        },
    }


# =========================================================================
# Metric 4: Context Precision（コンテキストの精度 / ランキング品質）
# =========================================================================
#
# 「関連する contexts は上位にランクされているか？」を測る。
#
# アルゴリズム: Average Precision (AP)
#   1. 各 context の関連性を判定（relevant / irrelevant）
#   2. 上位 k 位までの Precision@k を計算
#   3. AP = Σ(Precision@k × rel(k)) / (全関連数)
#
# 例:
#   contexts: [関連, 無関係, 関連, 無関係]
#   rel =     [1,     0,      1,     0   ]
#   k=1: P@1 = 1/1 = 1.0  (関連なので加算)
#   k=3: P@3 = 2/3 = 0.67 (関連なので加算)
#   AP = (1.0 + 0.67) / 2 = 0.83
#
# 直感: 関連 context が 1 位に来ると最高スコア、下位に来ると低スコア

async def context_precision(query: str, contexts: list[str], response: str) -> dict:
    """
    Context Precision (Average Precision) スコアを計算。

    Returns:
        {
            "score": 0.83,
            "details": {
                "relevance_binary": [1, 0, 1, 0],
                "total_relevant": 2,
                "precision_at_k": [{"k": 1, "precision": 1.0}, {"k": 3, "precision": 0.67}]
            }
        }
    """
    if not contexts:
        return {"score": 0.0, "details": {"reason": "no contexts provided"}}

    numbered = "\n\n".join(
        f"[Context {i + 1}]:\n{ctx}" for i, ctx in enumerate(contexts)
    )

    result = await _llm_json(
        system_prompt=(
            "You are a relevance judgment assistant.\n"
            "For each context chunk IN ORDER, determine if it is relevant to "
            "answering the given query.\n"
            '"relevant" = contains information that could help answer the query.\n'
            '"irrelevant" = has no useful information for the query.\n\n'
            "IMPORTANT: Evaluate each context in order (Context 1, 2, 3, ...).\n\n"
            "Return JSON:\n"
            '{"judgments": [\n'
            '  {"context_index": 1, "verdict": "relevant"},\n'
            '  {"context_index": 2, "verdict": "irrelevant"}\n'
            "]}"
        ),
        user_prompt=f"Query: {query}\n\n{numbered}",
    )

    judgments = result.get("judgments", [])

    # バイナリ関連性リストを構築
    relevance = []
    for i in range(len(contexts)):
        matching = [j for j in judgments if j.get("context_index") == i + 1]
        if matching:
            relevance.append(1 if matching[0].get("verdict") == "relevant" else 0)
        else:
            relevance.append(0)

    total_relevant = sum(relevance)
    if total_relevant == 0:
        return {
            "score": 0.0,
            "details": {"reason": "no relevant contexts found", "relevance_binary": relevance},
        }

    # Average Precision を計算
    precision_sum = 0.0
    running_relevant = 0
    precision_at_k = []

    for k in range(len(relevance)):
        if relevance[k] == 1:
            running_relevant += 1
            p_at_k = running_relevant / (k + 1)
            precision_sum += p_at_k
            precision_at_k.append({"k": k + 1, "precision": round(p_at_k, 4)})

    score = precision_sum / total_relevant

    return {
        "score": round(score, 4),
        "details": {
            "relevance_binary": relevance,
            "total_relevant": total_relevant,
            "precision_at_k": precision_at_k,
        },
    }


# =========================================================================
# Metric 5: Context Recall（コンテキストの再現率）— GT 必須
# =========================================================================
#
# 「正解（ground truth）に含まれる情報は、検索結果に含まれているか？」を測る。
#
# アルゴリズム:
#   Step 1: ground truth を個々の「文（statement）」に分解
#   Step 2: 各文が contexts にカバーされているか LLM に判定
#   Step 3: スコア = (カバーされた文数) / (全文数)
#
# なぜ GT が必要か:
#   - 「何が正解か」を知らないと「取りこぼし」を測定できない
#   - 現在のテストセットは GT なし → このメトリクスは score=None になる

async def context_recall(
    query: str, contexts: list[str], response: str, ground_truth: str
) -> dict:
    """
    Context Recall スコアを計算。GT がないと score=None。

    Returns:
        {
            "score": 0.75,  # or None if no GT
            "details": {
                "total_statements": 4,
                "covered_statements": 3,
                "verdicts": [{"statement": "...", "verdict": "covered/not_covered", "reason": "..."}, ...]
            }
        }
    """
    if not ground_truth:
        return {"score": None, "details": {"reason": "ground_truth not provided (skipped)"}}

    if not contexts:
        return {"score": 0.0, "details": {"reason": "no contexts to check against"}}

    combined_context = "\n\n".join(contexts)

    # --- Step 1: GT を文に分解 ---
    decompose_result = await _llm_json(
        system_prompt=(
            "You are a statement extraction assistant.\n"
            "Break down the given ground truth answer into individual, "
            "atomic factual statements.\n"
            "Each statement should be independently verifiable.\n\n"
            'Return JSON: {"statements": ["statement1", "statement2", ...]}'
        ),
        user_prompt=f"Ground truth:\n{ground_truth}",
    )

    statements = decompose_result.get("statements", [])
    if not statements:
        return {"score": 1.0, "details": {"reason": "no statements in ground truth"}}

    # --- Step 2: 各 GT 文が contexts にカバーされるか ---
    verify_result = await _llm_json(
        system_prompt=(
            "You are a coverage verification assistant.\n"
            "For each ground truth statement, determine if it is covered by the context.\n"
            '"covered" = the context contains information to derive or confirm it.\n'
            '"not_covered" = the context lacks this information.\n\n'
            "Return JSON:\n"
            '{"verdicts": [\n'
            '  {"statement": "...", "verdict": "covered", "reason": "brief reason"},\n'
            '  {"statement": "...", "verdict": "not_covered", "reason": "brief reason"}\n'
            "]}"
        ),
        user_prompt=(
            f"Context:\n{combined_context}\n\n"
            f"Ground truth statements:\n{json.dumps(statements, ensure_ascii=False)}"
        ),
    )

    verdicts = verify_result.get("verdicts", [])
    covered = sum(1 for v in verdicts if v.get("verdict") == "covered")
    total = len(statements)
    score = covered / total if total > 0 else 0.0

    return {
        "score": round(score, 4),
        "details": {
            "total_statements": total,
            "covered_statements": covered,
            "not_covered": total - covered,
            "verdicts": verdicts,
        },
    }


# =========================================================================
# Metric 6: Hallucination Detection（幻覚検出）
# =========================================================================
#
# 「回答に、contexts にない情報（幻覚）が含まれていないか？」を検出する。
#
# Faithfulness の裏返し:
#   - Faithfulness = 裏付けられた割合（高いほど良い）
#   - Hallucination = 裏付けられていない割合（低いほど良い）
#   - Hallucination Score = 1.0 - Faithfulness Score
#
# 追加価値: 具体的にどの claim が幻覚かをリストアップする
# → デバッグやプロンプト改善に直結する情報

async def hallucination_detection(
    query: str, contexts: list[str], response: str
) -> dict:
    """
    Hallucination スコアを計算（低いほど良い）。

    内部で faithfulness() を呼ぶため、追加の LLM コストはゼロ。

    Returns:
        {
            "score": 0.15,  # 低いほど良い
            "details": {
                "total_claims": 10,
                "hallucinated_claims_count": 2,
                "hallucinated_claims": [{"claim": "...", "reason": "..."}, ...],
                "faithfulness_score": 0.85
            }
        }
    """
    # Faithfulness の結果を再利用（追加 LLM コール 0）
    faith_result = await faithfulness(query, contexts, response)

    faith_score = faith_result["score"]
    details = faith_result["details"]

    # 幻覚スコア = 1 - 忠実性スコア
    hallucination_score = round(1.0 - faith_score, 4)

    # 具体的にどの claim が幻覚か抽出
    hallucinated_claims = [
        {"claim": v.get("claim", ""), "reason": v.get("reason", "")}
        for v in details.get("verdicts", [])
        if v.get("verdict") == "unsupported"
    ]

    return {
        "score": hallucination_score,
        "details": {
            "total_claims": details.get("total_claims", 0),
            "hallucinated_claims_count": len(hallucinated_claims),
            "hallucinated_claims": hallucinated_claims,
            "faithfulness_score": faith_score,
        },
    }


# =========================================================================
# evaluate_sample — 全メトリクスをまとめて実行
# =========================================================================
#
# 最適化ポイント:
#   1. Faithfulness → Hallucination は同じ結果を共有（LLM コール 0 追加）
#   2. 独立したメトリクスは asyncio.gather で並列実行
#   3. Context Recall は GT がある場合のみ実行

async def evaluate_sample(
    query: str,
    contexts: list[str],
    response: str,
    ground_truth: str | None = None,
) -> dict:
    """
    1 サンプルに対して全 6 メトリクスを実行。

    Args:
        query:        ユーザーの質問
        contexts:     検索で取得したコンテキスト（文字列のリスト）
        response:     Agent の最終回答
        ground_truth: 正解回答（オプション）

    Returns:
        {
            "faithfulness": {"score": ..., "details": ...},
            "answer_relevancy": {"score": ..., "details": ...},
            "context_relevance": {"score": ..., "details": ...},
            "context_precision": {"score": ..., "details": ...},
            "context_recall": {"score": ..., "details": ...},
            "hallucination_detection": {"score": ..., "details": ...},
        }
    """
    # --- Faithfulness を先に実行（Hallucination が結果を再利用するため） ---
    faith_result = await faithfulness(query, contexts, response)

    # --- Hallucination を Faithfulness から導出（追加コスト 0） ---
    faith_score = faith_result["score"]
    faith_details = faith_result["details"]
    hallucinated_claims = [
        {"claim": v.get("claim", ""), "reason": v.get("reason", "")}
        for v in faith_details.get("verdicts", [])
        if v.get("verdict") == "unsupported"
    ]
    hallucination_result = {
        "score": round(1.0 - faith_score, 4),
        "details": {
            "total_claims": faith_details.get("total_claims", 0),
            "hallucinated_claims_count": len(hallucinated_claims),
            "hallucinated_claims": hallucinated_claims,
            "faithfulness_score": faith_score,
        },
    }

    # --- 残りのメトリクスを並列実行 ---
    tasks = [
        answer_relevancy(query, contexts, response),
        context_relevance(query, contexts, response),
        context_precision(query, contexts, response),
    ]

    if ground_truth:
        tasks.append(context_recall(query, contexts, response, ground_truth))
        relevancy_res, ctx_rel_res, ctx_prec_res, ctx_rec_res = await asyncio.gather(
            *tasks
        )
    else:
        relevancy_res, ctx_rel_res, ctx_prec_res = await asyncio.gather(*tasks)
        ctx_rec_res = {"score": None, "details": {"reason": "ground_truth not provided"}}

    return {
        "faithfulness": faith_result,
        "answer_relevancy": relevancy_res,
        "context_relevance": ctx_rel_res,
        "context_precision": ctx_prec_res,
        "context_recall": ctx_rec_res,
        "hallucination_detection": hallucination_result,
    }
