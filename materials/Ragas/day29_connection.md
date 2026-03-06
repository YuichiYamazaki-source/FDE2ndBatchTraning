# Why This Work? — Connection to Day 29

**Related Lecture**: Day 29 — GenAI System Evaluation & Framework
**Lecture Note**: [[Lecture/day29-GenAI System Eva & Framework/GenAI System Evaluation & Framework]]

---

## Day 29 で学んだこと（前提）

Day 29 では、GenAI システムの評価がモデル単体ではなく **パイプライン全体** に対して行う必要があることを学んだ。

```
User Input → Prompt Engineering → Retrieval (Vector DB) → LLM → Output → Guardrails
```

> "Powerful models cannot rescue poor retrieval"

RAG システムにおいては、**Retrieval の品質** と **Generation の品質** を分離して評価することが重要であり、そのための定量的なメトリクスが存在する。

| カテゴリ | メトリクス | 何を測るか |
| --- | --- | --- |
| Generation | Faithfulness | LLM がコンテキスト外の情報を混入させていないか |
| Generation | Answer Relevance | 回答が質問に対してトピック的に関連しているか |
| Retrieval | Context Relevance | 取得されたコンテキストが質問に関連しているか |
| Retrieval | Context Recall | 正解に必要な情報を Retriever が取得できたか |
| Retrieval | Context Precision | 関連文書が上位にランキングされているか |
| Overall | Answer Semantic Similarity | 生成回答と Ground Truth の意味的類似度 |
| Overall | Answer Correctness | 生成回答が事実レベルで正確か |

---

## なぜこのワークをやるか

### 1. 座学で終わらせないため

Day 29 で学んだメトリクスの定義（Faithfulness、Context Recall など）は、式として理解するだけでは不十分。
**Ragas ライブラリを実際に動かして数値を出す体験**を通じて、それぞれのメトリクスが何をどう測っているかを体で理解する。

### 2. RAG パイプラインの「どこが壊れているか」を特定できるようにするため

RAG システムで精度が低い場合、原因は大きく 2 つある。

- **Retriever が悪い**: 関連文書を取得できていない → Context Recall / Context Relevance が低い
- **Generator が悪い**: コンテキストを無視・誤解している → Faithfulness / Answer Relevance が低い

Ragas を使いこなすことで、問題の原因を **定量的に切り分ける**スキルを習得する。

### 3. Ground Truth なしで評価できる範囲を知るため

Day 29 の学びの中で、メトリクスを「Ground Truth が必要かどうか」で分類できることがポイントだった。

- **GT 不要**: Faithfulness / Answer Relevance / Context Relevance
  → 開発初期・ラベルなし環境でも評価を回せる
- **GT 必要**: Context Recall / Context Precision / Answer Semantic Similarity / Answer Correctness
  → テストデータセットの設計が必要

このワークを通じて、**状況に応じた評価戦略の選び方**を実践的に身につける。

### 4. LLM-as-a-Judge の仕組みを実装レベルで理解するため

Faithfulness の claim 抽出や Context Relevance の判定など、Ragas の内部では LLM が評価を行っている。
実装を通じて「評価自体が LLM に依存している」構造を理解し、その限界（バイアス・ランダム性）も踏まえた上で使えるようになる。

---

## このワークで目指すアウトカム

- Ragas を使って RAG パイプラインの各メトリクスを計算できる
- スコアの意味を正しく解釈し、改善箇所を特定できる
- Ground Truth の有無に応じた評価設計ができる
