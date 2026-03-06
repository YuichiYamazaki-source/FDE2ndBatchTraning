# Task5: Orchestrated LLM Application — News Credibility Checker

**Date**: 2026-03-03
**Assignment**: Multi-Source News Credibility Checker with Agent Architecture

---

## 学んだこと

### 1. Agent と Tool の違い

| 種別 | 役割 | LLM使用 | 例 |
|------|------|---------|-----|
| **Agent** | 推論・判断・決定 | あり | Claim Decomposer, Scoring Agent |
| **Tool** | I/O処理・API呼び出し | なし | Web Search Tool, RAG Tool |

> **原則**: Tools は推論しない。Agents はAPIを直接呼ばない（必ずToolを経由）

---

### 2. シングルエージェントの限界

MVP (`minimal_mvp/main.py`) の問題点:

- **1回のLLMコールで全部やろうとする** → 推論が浅くなる
- **ソース品質が全部同一扱い** → 信頼性の高低が反映されない
- **矛盾検出が表面的** → 「矛盾あり」の一言で終わる
- **スコアの根拠が不透明** → なぜその点数か説明できない
- **再検索しない** → 証拠が薄くても1回で完了

---

### 3. 段階的な評価の改善

```
MVP (1 LLM call)
 ↓
Step 1: Claim Decomposition を追加
        クレームを構造化 → targeted search queries を生成
 ↓
Step 2: Source Scoring
 ↓
Step 3: Contradiction Detection
 ↓
Step 4: Scoring Agent (weighted composite)
```

#### Step 1: Claim Decomposition のポイント

入力クレームを以下に分解する:

```json
{
  "subject": "主語エンティティ",
  "predicate": "主張している行為・関係",
  "object": "主語について主張されていること",
  "domain": "medical | political | scientific | ...",
  "timeframe": "いつのことか",
  "search_queries": [
    "支持側の角度で検索するクエリ",
    "否定・反論側の角度で検索するクエリ",
    "専門家・科学的コンセンサスの角度"
  ]
}
```

**なぜ重要か**: LLMに「検索して」と任せると確証バイアスが入りやすい。
事前に「支持・反論・専門家」の3角度を明示することで、バランスの取れた証拠収集ができる。

---

### 4. Pipeline Evaluation (B) の設計

評価の方向性:

| 種別 | 内容 |
|------|------|
| **A: Pipeline評価** | 既知の正解があるクレームでシステムの精度を測る（精度・再現率） |
| **B: Agent強化** | 評価プロセス自体を多段にして説明可能にする |

テストセットの設計ポイント:
- **明確なミスインフォ** (score_max: 10) — "Earth is flat"
- **医学的デマ** (score_max: 15) — "vaccines cause autism"
- **明白な事実** (score_min: 90) — "Eiffel Tower is in Paris"
- **グレーゾーン** (score 20-70) — "8 glasses of water per day"

グレーゾーンが一番難しい。LLMは「Contested」と正しく判断できるか？

---

### 5. Microservices Architecture の設計方針

```
Meta Agent (オーケストレーター)
    │
    ├── Claim Decomposer Agent   → search_queries 生成
    ├── Source Selection Agent   → どのソースを使うか
    ├── Filter Agent             → LLMレベル関連性スコアリング
    ├── Reputation Agent         → ソース・著者の信頼性
    ├── Contradiction Agent      → クロスソース比較
    ├── Critique Agent           → 弱い主張への再検索ループ (max 2回)
    └── Scoring Agent            → 最終スコア合成
```

#### Agent vs Tool 分類

| コンポーネント | 種別 | 理由 |
|---|---|---|
| Web Search | Tool | 検索結果を返すだけ、推論なし |
| Pre-filter | Tool | ルールベース（blacklist・重複除去） |
| RAG | Tool | Vector DB の read/write |
| Source Registry | Tool | 設定データの参照 |
| Claim Decomposer | Agent | 構造化・クエリ生成に推論が必要 |
| Contradiction Detector | Agent | ソース間の比較判断が必要 |

#### Critique Loop の設計

```
CritiqueAgent
    ├── 証拠が十分 → "resolved" → Scoring Agent へ
    └── 証拠が不十分 → follow-up queries → WebSearch (max 2回)
                        2回超えたら "UNRESOLVED" で打ち切り
```

---

### 6. 実装ファイル構成

```
Orchestrated LLM Application/
├── minimal_mvp/
│   └── main.py          ← シングルエージェントのMVP
├── step1_eval/
│   └── main.py          ← Step1 (Decomposition) + Pipeline Eval 追加
└── Task5_NewsCredibilityChecker_Architecture.md
```

#### `step1_eval/main.py` で追加した内容

| 関数 | 種別 | 説明 |
|------|------|------|
| `decompose_claim()` | **[NEW]** | クレームを分解してsearch_queries生成 |
| `check_credibility()` | **[UPDATED]** | decompositionを受け取りtargeted queriesで検索 |
| `evaluate_pipeline()` | **[NEW]** | テストケースで精度測定 |
| `run_single()` | **[NEW]** | Step1+Step2を順に実行するラッパー |

---

### 7. Open Questions (未解決)

- [ ] RAGバックエンド: ChromaDB（ローカル）vs Pinecone（マネージド）
- [ ] Source Registry の更新頻度: 静的設定 vs LLMによる定期更新
- [ ] Critique Loop のトリガー: 常時 / 低信頼度のみ / ユーザー選択
- [ ] コスト管理: トークン上限 / クレーム単位の金額上限

---

## 関連ファイル

- [[Task5_NewsCredibilityChecker_Architecture]] — アーキテクチャ図 (Mermaid)
- `materials/Orchestrated LLM Application/minimal_mvp/main.py`
- `materials/Orchestrated LLM Application/step1_eval/main.py`

---

## 🔗 Graph Links

- 🗺️ MOC: [[MOC]]
- Related Lecture (Orchestration) → [[Lecture/day24-FDE skills & LLM Orchestration/LLM Orchestration]]
- Related Lecture (LangGraph/LangChain) → [[Lecture/day25-LangChain/LLM Orchestration with LangChain]]
- Related Lecture (Agentic AI) → [[Lecture/day26-Agentic AI & RAG/Agentic AI & RAG]]
- Related Lecture (MCP) → [[Lecture/day27-Agent Protocols & Advanced Use Cases/Agent Protocols & Advanced Use Cases]]
- Related Lecture (Eval) → [[Lecture/day29-GenAI System Eva & Framework/GenAI System Evaluation & Framework]]
- Architecture doc → [[materials/Orchestrated LLM Application/Task5_NewsCredibilityChecker_Architecture]]

### 同じ概念を持つノート
- `#concept/multi-agent` → [[Lecture/day26-Agentic AI & RAG/Agentic AI & RAG]]
- `#concept/llm-as-judge` → [[Lecture/day24-FDE skills & LLM Orchestration/LLM Orchestration]]
- `#concept/rag-pipeline` → [[Lecture/day22-Context Engineering/Context Engineering & RAG]]
- `#concept/guardrails` → [[Lecture/day28-Securing LLMs & Guardrails/Securing LLMs & Guardrails]]
- `#concept/eval-framework` → [[Lecture/day29-GenAI System Eva & Framework/GenAI System Evaluation & Framework]]

### Capstone との接続
- Multi-Agent構成 / LLM Ops → [[Captone/README]]

---

## 🏷️ Tags

`#type/practice` `#domain/orchestration` `#domain/agent` `#domain/evaluation`
`#concept/multi-agent` `#concept/llm-as-judge` `#concept/rag-pipeline`
`#concept/agent-loop` `#concept/handoff` `#concept/evals`
`#status/in-progress`
