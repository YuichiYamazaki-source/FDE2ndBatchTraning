# Phase 4 — 評価（Evals）学習ノート

Phase 4 を進めながら学んだこと・気づきをここに蓄積する。

---

## A. Ragas メトリクス

### 評価に必要な 4 つのデータ

| データ | 説明 | GT なし評価 | GT あり評価 |
| ------ | ---- | ---------- | ---------- |
| query | ユーザーの質問 | 必要 | 必要 |
| contexts | Retriever が取得したコンテキスト | 必要 | 必要 |
| response | LLM が生成した回答 | 必要 | 必要 |
| ground_truth | 人間が用意した正解 | **不要** | **必要** |

### Retrieval 評価（検索品質）

| メトリクス | 問い | GT | 計算 |
| --------- | ---- | -- | ---- |
| Context Relevance | 検索結果は質問に関係あるか？ | 不要 | 関連文の数 / 全文数 |
| Context Recall | 正解に必要な情報を検索で拾えたか？ | 必要 | GT文のうちコンテキストにある数 / GT全文数 |
| Context Precision | 関連情報が検索結果の上位にあるか？ | 必要 | 関連文書の Precision@k の平均 |

### Generation 評価（生成品質）

| メトリクス | 問い | GT | 計算 |
| --------- | ---- | -- | ---- |
| Faithfulness | 回答はコンテキストに基づいているか？ | 不要 | コンテキストにある主張数 / 全主張数 |
| Answer Relevance | 回答は質問に答えているか？ | 不要 | 逆生成した質問と元質問のコサイン類似度 |

### Overall 評価

| メトリクス | 問い | GT |
| --------- | ---- | -- |
| Answer Semantic Similarity | 回答と正解の意味的類似度 | 必要 |
| Answer Correctness | 事実レベルの正確性（Semantic + F1） | 必要 |

### 気づき

- GT なし評価（Faithfulness / Answer Relevance / Context Relevance）は開発初期にすぐ使える
- Faithfulness が低い = ハルシネーション → Problem Statement の「hallucination detection」に対応
- Context Relevance が低い = 検索にノイズ → Embedding 戦略の見直しが必要
- Context Recall が低い = 正解情報を取りこぼし → 検索数やフィールド追加を検討

---

## B. OpenAI Agents SDK トレーシング

### トレースとは

Agent が 1 つの質問に答えるまでの**全ステップの記録**。SDK がデフォルトで自動記録する。

### 自動記録される情報

| 記録項目 | 内容 |
| ------- | ---- |
| LLM 入出力 | プロンプト・レスポンス |
| ツール呼び出し | 関数名・引数・返り値 |
| レイテンシ | 各ステップの所要時間 |
| トークン使用量 | input/output トークン数 |

### Ragas との接点

Ragas 評価に必要な query / contexts / response はトレースから自動抽出できる:

```
① query     ← Runner.run() の input
② contexts  ← search_products ツールの result
③ response  ← Runner.run() の final_output
④ ground_truth ← トレースにない。別途用意が必要。
```

### 気づき

- A（何を測るか）+ B（データをどう集めるか）= 評価パイプライン
- トレースなしでも評価可能だが、Agent 内部のステップが見えないため原因特定が難しい
- トレースはコスト分析（トークン量）やボトルネック特定（レイテンシ）にも使える

---

## C. Problem Statement の要求マッピング

| Problem Statement の要求 | Ragas メトリクス | GT | Phase |
| ----------------------- | --------------- | -- | ----- |
| context relevance | Context Relevance | No | 4 |
| retrieval precision | Context Precision | Yes | 4 |
| recall | Context Recall | Yes | 4 |
| faithfulness | Faithfulness | No | 4 |
| answer relevance | Answer Relevance | No | 4 |
| hallucination detection | Faithfulness（低スコア = ハルシネーション） | No | 4 |
| toxicity filtering | Guardrails で対応（Ragas ではない） | - | **6** |

### 気づき

- 6 要求のうち 5 つは Phase 4 で対応可能。toxicity だけ Phase 6
- hallucination detection は独立した仕組みではなく Faithfulness スコアそのもの

---

## D. 実行戦略

### 2 段階アプローチ

```
Phase 4a: GT なし評価（すぐ始められる）
  ├── Faithfulness
  ├── Answer Relevance
  └── Context Relevance

Phase 4b: GT あり評価（テストデータセット作成後）
  ├── Context Recall
  └── Context Precision
```

### テストデータセットの作り方

| 方法 | メリット | デメリット |
| ---- | ------- | --------- |
| 手動作成（10〜15件） | 品質が高い | 時間がかかる |
| Ragas Synthetic 生成 | 大量に作れる | 品質にばらつき |

推奨: 手動 10〜15 件 → Synthetic 50 件追加 → レビュー

### 実装順序

```
Step 1: evals/ に評価スクリプトの骨組み
Step 2: テストデータセット（質問リスト）を用意
Step 3: Agent 実行 → query / contexts / response を収集
Step 4: GT なしメトリクス実行
Step 5: 結果分析 → 低スコア箇所を特定
Step 6: Ground Truth 追加 → GT ありメトリクスも実行
Step 7: 全スコアをレポート化 → Phase 5 の設計判断
```

### 評価結果 → Phase 5 への繋がり

| 低スコアのメトリクス | Phase 5 対策例 |
| ------------------- | ------------- |
| Context Relevance/Recall | 専用 Search Agent、Embedding 戦略変更 |
| Faithfulness | Fact-Check Agent、プロンプト改善 |
| Answer Relevance | 質問分類 Agent で意図把握を改善 |

---

## E. Ragas をやめてスクラッチ実装した理由

### 問題: Ragas v0.4.3 の互換性問題

Ragas を使おうとして 3 つのエラーにハマった:

1. **`embed_query` エラー**: Ragas 内部の `ResponseRelevancy` メトリクスが
   `langchain_openai.OpenAIEmbeddings.embed_query()` を呼ぶが、
   Ragas ネイティブの `OpenAIEmbeddings` には `embed_text()` しかない
2. **`max_tokens` エラー**: Faithfulness の claim 抽出で gpt-4o-mini の
   出力が 3072 トークンを超えてしまう（長い回答で claim が多すぎる）
3. **deprecated API の混在**: `ragas.metrics` (旧) と `ragas.metrics.collections` (新) で
   `evaluate()` の isinstance チェックに互換性がない

### 根本原因: Ragas は langchain エコシステム前提

- Ragas は内部で `langchain_openai`, `langchain_core` を多用
- OpenAI Agent SDK (openai-agents) は langchain とは別系統
- この 2 つを無理に繋げるのが間違いだった

### 解決: LLM-as-Judge パターンで自作

Ragas がやってることの本質は **「LLM に評価させる」** だけ。
具体的には:

```
Faithfulness:
  1. gpt-4o-mini に「回答を claim に分解して」と頼む
  2. gpt-4o-mini に「各 claim が contexts にあるか判定して」と頼む
  3. supported / total = スコア

Answer Relevancy:
  1. gpt-4o-mini に「回答から逆質問を 3 個生成して」と頼む
  2. text-embedding-3-small で元の質問と逆質問の embedding を取得
  3. コサイン類似度の平均 = スコア
```

これなら OpenAI API を直接叩くだけでいい。langchain 不要。

### メリット

| 項目 | Ragas | 自作 |
| ---- | ----- | ---- |
| 依存パッケージ | ragas + langchain + 20個以上 | openai のみ |
| デバッグ | ブラックボックス | プロンプトが見える |
| カスタマイズ | 限定的 | 自由自在 |
| API コスト | 同じ (gpt-4o-mini) | 同じ |
| 互換性問題 | あり（v0.4.3） | なし |

---

## F. カスタムメトリクスの実装詳細

### ファイル構成

```
evals/
  metrics.py          ← 6 メトリクスの実装（OpenAI API のみ）
  eval_runner.py      ← パイプライン（Steps 1-5）
  testset.json        ← テストデータ（15 問）
  results/
    collected_latest.json  ← Agent 実行結果（中間データ）
    eval_YYYYMMDD_*.json   ← 評価結果
```

### 共有ヘルパー

#### `_llm_json(system, user)` — JSON mode で LLM 呼び出し

```python
# OpenAI の response_format={"type": "json_object"} を使うと
# LLM は必ず有効な JSON を返す → パースエラーが起きない
resp = await client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type": "json_object"},
    messages=[...],
    temperature=0.0,  # 決定的な判定
)
```

**ポイント**: `temperature=0.0` で毎回同じ判定を返す（評価の再現性）

#### `_get_embeddings(texts)` — バッチ embedding

```python
# N テキストを 1 API コールで一括処理
resp = await client.embeddings.create(
    model="text-embedding-3-small",
    input=["text1", "text2", "text3"],  # リストで渡す
)
```

**コスト最適化**: Answer Relevancy で query + 3 逆質問 = 4 テキストを 1 コールで処理

#### `_cosine_similarity(a, b)` — コサイン類似度

```python
# numpy を使わず pure Python で実装（依存ゼロ）
dot = sum(x * y for x, y in zip(a, b))
norm_a = sqrt(sum(x * x for x in a))
norm_b = sqrt(sum(x * x for x in b))
similarity = dot / (norm_a * norm_b)
```

### 各メトリクスの仕組み

#### 1. Faithfulness（忠実性）— 2 LLM calls

**質問**: 「回答は検索結果に基づいているか？」

```
Step 1: 回答 → claim 分解
  "Chair A は $50 で評価 4.5" → ["Chair A は $50", "Chair A の評価は 4.5"]

Step 2: 各 claim を contexts と照合
  "Chair A は $50" → contexts に "$50" あり → supported
  "配送は無料"     → contexts に記載なし    → unsupported

Step 3: score = supported / total = 2/3 = 0.67
```

**分けてる理由**: 1 回で「分解 + 判定」をやると出力が長くなりすぎて
max_tokens エラーになる（Ragas で実際に起きた問題）

#### 2. Answer Relevancy（回答の関連性）— 1 LLM + 1 embed

**質問**: 「回答は質問に対して適切か？」

```
Step 1: 回答から逆質問を 3 個生成
  回答: "Here are office chairs under $200..."
  → ["What are office chairs under $200?",
     "Can you recommend affordable office chairs?",
     "What chairs are available for a budget?"]

Step 2: embedding でコサイン類似度を計算
  元の質問 ↔ 逆質問1: 0.85
  元の質問 ↔ 逆質問2: 0.66
  元の質問 ↔ 逆質問3: 0.44

Step 3: score = mean(0.85, 0.66, 0.44) = 0.65
```

**直感**: 良い回答から生成された逆質問は元の質問に近い

#### 3. Context Relevance（コンテキストの関連性）— 1 LLM call

**質問**: 「検索結果は質問に関連しているか？」

```
質問: "office chair under $200"
Context 1: "[123] Office Chair $50 ⭐4.5" → relevant
Context 2: "[456] Yoga Mat $20 ⭐4.8"     → irrelevant

score = 1/2 = 0.50
```

**全 context を 1 回のコールでまとめて判定**（コスト節約）

#### 4. Context Precision（ランキング品質）— 1 LLM call

**質問**: 「関連する context は上位にあるか？」

```
contexts: [関連, 無関係, 関連, 無関係]
rel =     [1,     0,      1,     0   ]

k=1: P@1 = 1/1 = 1.0  (1位が関連 → 加算)
k=3: P@3 = 2/3 = 0.67 (3位が関連 → 加算)
AP = (1.0 + 0.67) / 2 = 0.83
```

**Average Precision**: 関連 context が上位にあるほど高スコア

#### 5. Context Recall（再現率）— 2 LLM calls, GT 必須

**質問**: 「正解の情報は検索結果に含まれているか？」

```
GT: "Chair A は $50 で防水。" → ["Chair A は $50", "Chair A は防水"]
Context: "[123] Chair A $50 ⭐4.5"

"Chair A は $50" → covered
"Chair A は防水" → not_covered (contexts に防水の記載なし)

score = 1/2 = 0.50
```

**現状**: testset.json の ground_truth が全て null → score=None（スキップ）

#### 6. Hallucination Detection（幻覚検出）— 0 追加 calls

**質問**: 「回答に、検索結果にない情報（幻覚）があるか？」

```
Faithfulness の結果を再利用:
  score = 1.0 - faithfulness_score

さらに、具体的な幻覚 claim のリストも返す:
  hallucinated_claims: [{"claim": "配送は無料", "reason": "contexts にない"}]
```

**Faithfulness と同じ claim 分析を共有 → 追加 LLM コスト 0**

### API コスト（15 サンプル、GT なし）

| リソース | 1サンプル | 15サンプル合計 | コスト |
| ------- | -------- | ------------ | ----- |
| gpt-4o-mini | 5 calls | 75 calls | ~$0.06 |
| text-embedding-3-small | 1 call | 15 calls | ~$0.001 |
| **合計** | | | **~$0.06** |

### 最適化ポイント

1. **Faithfulness + Hallucination 共有**: claim 分析 1 回で 2 メトリクス算出
2. **embedding バッチ化**: query + 3 逆質問を 1 API コールで処理
3. **独立メトリクスの並列実行**: `asyncio.gather()` で同時に API コール

---

## G. 初回評価結果の分析

### 結果サマリ（2026-03-05）

```
faithfulness              [###########.........] 0.577
answer_relevancy          [##########..........] 0.538
context_relevance         [##########..........] 0.500
context_precision         [##########..........] 0.500
context_recall            [     N/A (no GT)    ]  ---
hallucination_detection   [########............] 0.423
```

### スコアが低めに出る原因

15 サンプル中、**6 サンプルは contexts が空**（`get_product` / `analyze_reviews` を
使ったため `search_products` が呼ばれず、context がキャプチャされない）。

contexts が空の場合:
- Faithfulness = 0.0（裏付ける context がない）
- Context Relevance = 0.0（評価対象がない）
- Hallucination = 1.0（全 claim が「裏付けなし」扱い）

→ これらが全体平均を押し下げている

### Phase 5 への示唆

| 観察 | 対策案 |
| ---- | ------ |
| contexts 空のサンプルがスコアを下げる | get_product/analyze_reviews の結果も context としてキャプチャする |
| Faithfulness 0.577 | Agent のプロンプトで「検索結果に基づいて回答せよ」を強化 |
| Context Relevance 0.500 | Embedding モデルの見直し or 検索クエリのリライト |
