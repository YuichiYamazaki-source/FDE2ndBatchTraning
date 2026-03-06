# Ragas Project Memory

## Overview

**Project**: GenAI-Powered E-Commerce Product Discovery and Assistance System
**Working dir**: `c:\Users\yuila\Documents\FDE2ndBatchTraning\materials\Ragas\`
**Dataset**: `Project/walmart-products.xlsx`

---

## Key Reference Files (セッション開始時に参照)

| File | Purpose |
| ---- | ------- |
| `README.md` | Tech stack / Phase 状態 / プロジェクト構造 |
| `ARCHITECTURE.md` | Mermaid アーキテクチャ図 / API 定義 / データフロー |
| `docker-compose.yml` | サービス構成・ポート・ボリューム設定（書き方は `C:\Users\yuila\Documents\FDE2ndBatchTraning\docker-compose.yml` を参照） |
| `day29_connection.md` | Day 29 Ragas 評価メトリクスの背景 |
| `Project/Problem Statement *.pdf` | **課題の正式仕様書（必読）。実装前に必ず参照すること** |

---

## Development Plan (Phase順に実装、出戻り厳禁)

| Phase | 内容 | 状態 |
| ----- | ---- | ---- |
| 1 | Backend (Agent なし) — Docker-compose + ChromaDB + API 層 | ✅ |
| 2 | Frontend — 最小構成 + Agent 枠のプレースホルダー | ✅ |
| 3 | Agent 最小構成 — Single Agent + シンプル RAG で動作確認 | ✅ |
| 4 | Evals — Ragas で評価実装・分析 | ⬜ |
| 5 | Multi-Agent — Evals 分析に基づき設計 → 実装 | ⬜ |
| 6 | Guardrails — ユーザー OK 後にシステム全体を再確認して設計 | ⬜ |

**実装方針**: 常にフルプランを意識する。後フェーズの拡張ポイントを前フェーズで設計に織り込み、出戻りを防ぐ。

---

## Tech Stack (確定)

| Layer | Technology |
| ----- | ---------- |
| Frontend | React + Vite (:5173) |
| Backend | FastAPI (:8000) |
| Vector DB | ChromaDB (:8001) — `./chroma_data/` にローカル永続化 |
| Embedding | text-embedding-3-small (OpenAI) |
| LLM | gpt-4o-mini (Phase 1–4) → gpt-4o (Phase 5+) |
| Agent Framework | OpenAI Agents SDK (Phase 3+) |
| Evaluation | Ragas (Phase 4+) |
| Infrastructure | Docker Compose |

---

## Backend Structure

```text
backend/
├── main.py              # FastAPI entry point, CORS
├── routers/             # search.py / products.py / chat.py / images.py
├── services/            # rag_service.py / product_service.py / llm_service.py
├── models/schemas.py    # Pydantic request/response models
├── core/config.py       # pydantic-settings (env vars)
├── ai_agents/           # Phase 3 — Orchestrator Agent (single-agent MVP)
│   ├── orchestrator.py  # Agent + run_orchestrator()
│   └── tools.py         # 4 @function_tool: search / get / analyze / recommend
└── guardrails/          # Phase 6
```

## Design Decisions

- ChromaDB は別 Docker サービス (`chromadb/chroma:0.5.23`) として起動、HttpClient で接続（クライアントとバージョン一致が必須）
- `chat.py` → `from ai_agents.orchestrator import run_orchestrator` で Agent に接続済み
- Agent 層は `backend/ai_agents/` に配置。`agents` は openai-agents SDK のパッケージ名なので `ai_agents` を使う
- `openai>=1.87.0` が必要（openai-agents==0.0.19 の依存）
- **画像プロキシ**: Walmart CDN (`i5.walmartimages.com`) はブラウザからの直接リクエストをリファラー/CORS でブロックする。`/api/image-proxy?url=...` でバックエンド経由で画像を取得し返す方式で解決。フロントエンドは `proxyImageUrl()` ヘルパー (`api/client.js`) で URL を変換

## Embedding Strategy

- 対象フィールド（Problem Statement Section 9 準拠）: `product_name`, `description`, `specifications`, `ingredients`, `customer_reviews`, `category_name`
- フィールドラベル付き結合: `"product_name: X description: Y ..."` （1商品 = 1ベクトル）
- ラベルを付ける理由: embedding モデルがフィールド境界を認識しやすくなる
- 将来のフィールド別チャンキングへの移行が容易（ラベルで分割するだけ）
- Phase 4 の Ragas 評価で `context_recall` が低ければ戦略を見直す

## Testing Policy

- **Backend (Python)**: pytest を使ってフェーズごとに逐次テストを書く
- **Frontend (JS/TS)**: Vitest (Jest 互換 API) を使ってコンポーネント・ロジックをテスト
- 実装の都度テストを追加し、Claude がテストを実行して確認してから次フェーズへ進む

### テスト実行コマンド

```bash
# Backend — ローカル (pytest.ini で testpaths 設定済み)
/c/Users/yuila/miniconda3/python.exe -m pytest -v

# Backend — Docker
docker compose run --rm pytest

# Frontend — Docker (--no-deps で frontend のみ起動)
docker compose run --rm --no-deps frontend npm test
```

### 結合テスト (Phase 3 完了後に実施)

- `docker compose up` で全サービス (backend / chromadb / frontend) を起動
- 最小構成シナリオを手動 or スクリプトで確認:
  1. `GET /api/health` → 200
  2. `POST /api/search` → ChromaDB から結果が返る
  3. `GET /api/products/{id}` → 商品詳細が返る
  4. `POST /api/chat` → Agent (Phase 3) の応答が返る
  5. ブラウザで `localhost:5173` → UI が表示され検索・チャットが動作する

## Frontend Structure (Phase 2)

```text
frontend/
├── src/
│   ├── App.jsx                  # ルート: state管理・API呼び出し
│   ├── api/client.js            # proxyImageUrl / searchProducts / getProduct / sendChat
│   ├── components/
│   │   ├── SearchBar.jsx        # 検索入力 + limit(1-15)
│   │   ├── Breadcrumb.jsx       # Home > Category > Subcategory > Product
│   │   ├── ProductCard.jsx      # 検索結果カード (クリックで詳細)
│   │   ├── ProductList.jsx      # カード一覧
│   │   ├── ProductDetail.jsx    # モーダル詳細 (JSON→専用コンポーネントで表示)
│   │   └── ChatPanel.jsx        # チャット (Phase 3 で Agent に差し替え)
│   └── test/                    # Vitest テスト (12 tests passing)
├── vite.config.js               # host:0.0.0.0, proxy: /api → backend:8000
└── Dockerfile
```

- `localhost:5173` → Frontend (ホストから直接アクセス可)
- Vite proxy で `/api` → `http://backend:8000` に転送 (docker-compose 内部)

## Study Guides

| File | 内容 |
| ---- | ---- |
| `docs/phase3_react_changes.md` | Phase 3 React 変更解説（画像プロキシ・JSON表示コンポーネント） |
| `docs/phase4_eval_learning.md` | Phase 4 評価の学習ノート（Ragas メトリクス・Agent 評価・気づき） |
