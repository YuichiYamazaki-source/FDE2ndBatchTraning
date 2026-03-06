# GenAI-Powered E-Commerce Product Discovery and Assistance System

## Overview

An AI-powered e-commerce platform that combines RAG (Retrieval-Augmented Generation) with an
intelligent agent architecture to enable natural language product discovery, AI-driven product
insights, and review-based recommendations.

## Tech Stack

| Layer | Technology |
| ----- | ---------- |
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| Vector DB | ChromaDB |
| Embedding Model | text-embedding-3-small (OpenAI) |
| LLM | gpt-4o-mini (Phase 1–4) → gpt-4o (Phase 5+) |
| Agent Framework | OpenAI Agents SDK (Phase 3+) |
| Evaluation | Ragas |
| Infrastructure | Docker Compose |

## Development Phases

| Phase | Description | Status |
| ----- | ----------- | ------ |
| 1 | Backend (no agents) — FastAPI + ChromaDB + data ingestion | ✅ |
| 2 | Frontend — minimal UI + agent placeholder slots | ✅ |
| 3 | Agent MVP — Single Agent + simple RAG, verify end-to-end | ✅ |
| 4 | Evals — Ragas metrics implementation and analysis | ⬜ |
| 5 | Multi-Agent — redesign based on eval results | ⬜ |
| 6 | Guardrails — full system review + safety layer | ⬜ |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system diagrams.

## Project Structure

```text
Ragas/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── routers/
│   │   ├── search.py        # POST /api/search
│   │   ├── products.py      # GET /api/products/{id}
│   │   ├── chat.py          # POST /api/chat (agent-powered)
│   │   └── images.py        # GET /api/image-proxy (CDN image proxy)
│   ├── services/
│   │   ├── rag_service.py   # ChromaDB query logic
│   │   ├── product_service.py
│   │   └── llm_service.py   # OpenAI calls
│   ├── models/
│   │   └── schemas.py       # Pydantic request/response models
│   ├── core/
│   │   └── config.py        # Environment variable settings
│   ├── ai_agents/           # Agent layer (Phase 3+)
│   │   ├── orchestrator.py  # Orchestrator Agent (single-agent MVP)
│   │   └── tools.py         # 4 function tools (search/get/analyze/recommend)
│   └── guardrails/          # Safety filters (Phase 6)
├── frontend/                # React + Vite application
├── docs/
│   └── phase3_react_changes.md  # Phase 3 React changes study guide
├── evals/                   # Ragas evaluation scripts (Phase 4+)
├── data/
│   └── ingest.py            # One-time script: xlsx → ChromaDB
├── chroma_data/             # ChromaDB persistent storage (gitignored)
├── docker-compose.yml
├── .env.example
└── README.md
```

## Embedding Strategy

Embedding fields (per Problem Statement Section 9):
`product_name`, `description`, `specifications`, `ingredients`, `customer_reviews`, `category_name`

Each field is prepended with a label (`field: value`) before concatenation into a single vector.

**Rationale**: Field labels help the embedding model recognize field boundaries, improving
semantic alignment with natural language queries. This keeps implementation simple (one vector
per product) while making field-level chunking straightforward in the future — each labeled
segment can be split and embedded independently if Ragas evaluation (Phase 4) indicates
retrieval quality needs improvement.

## Design Principles

- **Separation of Concerns**: Frontend / Backend / Agent layer are strictly decoupled
- **Microservice-ready**: Each service communicates via REST API; agent layer is plug-in
- **Incremental delivery**: Each phase is independently testable before moving to the next
- **Evaluation-driven**: Agent architecture decisions are made after Ragas analysis, not before

## Getting Started

```bash
# Start all services
docker compose up

# Backend API docs
http://localhost:8000/docs

# Frontend
http://localhost:5173
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```dotenv
OPENAI_API_KEY=sk-...
```
