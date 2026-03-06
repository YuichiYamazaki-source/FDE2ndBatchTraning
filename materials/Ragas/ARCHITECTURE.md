# System Architecture

## Current Architecture (Phase 1–2: No Agents)

```mermaid
flowchart TD
    User["User (Browser)"]
    FE["Frontend</br>React + Vite</br>:5173"]
    BE["Backend</br>FastAPI</br>:8000"]
    Chroma["ChromaDB</br>(Vector Store)"]
    OAI["OpenAI API</br>text-embedding-3-small</br>gpt-4o-mini"]
    Data["walmart-products.xlsx</br>(Product Data)"]

    User --> FE
    FE -->|REST| BE
    BE --> Chroma
    BE --> OAI
    Data -->|Ingest| Chroma
```

## Current Architecture (Phase 3: Single Agent MVP)

```mermaid
flowchart TD
    User["User (Browser)"]
    FE["Frontend<br/>React + Vite<br/>:5173"]
    BE["Backend<br/>FastAPI<br/>:8000"]
    Orch["Orchestrator Agent<br/>(gpt-4o-mini)"]
    Tools["Function Tools<br/>search_products<br/>get_product<br/>analyze_reviews<br/>recommend_alternatives"]
    Chroma["ChromaDB<br/>:8001"]
    OAI["OpenAI API<br/>Embedding + LLM"]
    Proxy["Image Proxy<br/>/api/image-proxy"]

    User --> FE
    FE -->|"REST /api/search<br/>/api/chat"| BE
    FE -->|"/api/image-proxy"| Proxy
    Proxy -->|"Server-side fetch"| WalmartCDN["Walmart CDN"]
    BE -->|"POST /api/chat"| Orch
    Orch --> Tools
    Tools --> Chroma
    Tools --> OAI
    BE -->|"POST /api/search"| Chroma
    BE -->|"embed(query)"| OAI
```

## Phase 4: Evaluation Pipeline

```mermaid
flowchart LR
    subgraph "Step 1: Data Collection"
        QA["Test Dataset<br/>(query + ground_truth)"]
        Agent["Orchestrator Agent"]
        Trace["Trace Data<br/>query / contexts / response"]
    end

    subgraph "Step 2: Ragas Evaluation"
        GTFree["GT-Free Metrics<br/>Faithfulness<br/>Answer Relevance<br/>Context Relevance"]
        GTReq["GT-Required Metrics<br/>Context Recall<br/>Context Precision"]
    end

    subgraph "Step 3: Analysis"
        Report["Score Report<br/>(JSON + Summary)"]
        Decision["Phase 5 Design<br/>Decisions"]
    end

    QA -->|"query"| Agent
    Agent -->|"auto-extract"| Trace
    Trace --> GTFree
    Trace -->|"+ ground_truth"| GTReq
    GTFree --> Report
    GTReq --> Report
    Report --> Decision
```

## Phase 4: Evaluation Data Flow

```mermaid
sequenceDiagram
    participant DS as Test Dataset
    participant Eval as eval_runner.py
    participant Agent as Orchestrator Agent
    participant Chroma as ChromaDB
    participant OAI as OpenAI API
    participant Ragas as Ragas Library

    DS->>Eval: Load questions (query + ground_truth)
    loop For each question
        Eval->>Agent: Runner.run(query)
        Agent->>Chroma: search_products(query)
        Chroma-->>Agent: product contexts
        Agent->>OAI: Generate response
        OAI-->>Agent: response text
        Agent-->>Eval: final_output + tool results
        Eval->>Eval: Extract (query, contexts, response)
    end
    Eval->>Ragas: EvaluationDataset + metrics
    Ragas->>OAI: LLM-as-Judge (claim extraction, etc.)
    OAI-->>Ragas: judgments
    Ragas-->>Eval: Scores per metric
    Eval->>Eval: Save report (JSON + analysis)
```

## Target Architecture (Phase 5: Multi-Agent)

```mermaid
flowchart TD
    User["User (Browser)"]
    FE["Frontend</br>React + Vite"]
    BE["Backend</br>FastAPI"]
    Orch["Orchestrator Agent"]
    RAGAgent["Retrieval Agent</br>(RAG)"]
    AnalysisAgent["Product Analysis Agent"]
    RecAgent["Recommendation Agent"]
    Chroma["ChromaDB"]
    OAI["OpenAI API</br>gpt-4o"]
    Guard["Guardrails</br>(Phase 6)"]

    User --> FE
    FE -->|REST| BE
    BE --> Guard
    Guard --> Orch
    Orch --> RAGAgent
    Orch --> AnalysisAgent
    Orch --> RecAgent
    RAGAgent --> Chroma
    RAGAgent --> OAI
    AnalysisAgent --> OAI
    RecAgent --> Chroma
    RecAgent --> OAI
```

## API Endpoints (Phase 1 target)

| Method | Path | Description |
| ------ | ---- | ----------- |
| POST | `/api/search` | Natural language product search (RAG) |
| GET | `/api/products/{product_id}` | Get product detail by ID |
| POST | `/api/chat` | Product chatbot (placeholder in Phase 1) |
| GET | `/api/health` | Health check |

> Agent-backed endpoints (`/api/chat`, `/api/recommend`) return stub responses in Phase 1–2
> and are connected to real agents in Phase 3+.

## Data Flow: Product Search

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant BE as FastAPI
    participant OAI as OpenAI Embedding
    participant DB as ChromaDB

    U->>FE: "Show me organic skincare under $30"
    FE->>BE: POST /api/search {query, limit}
    BE->>OAI: embed(query)
    OAI-->>BE: query_vector
    BE->>DB: similarity_search(query_vector, n=limit)
    DB-->>BE: top-k products
    BE-->>FE: [{product_name, price, rating, ...}]
    FE-->>U: Product cards
```

## Data Flow: Chatbot (Phase 3+)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant BE as FastAPI
    participant Orch as Orchestrator Agent
    participant Analysis as Analysis Agent
    participant Rec as Recommendation Agent
    participant DB as ChromaDB

    U->>FE: "Is this product good?" + product_id
    FE->>BE: POST /api/chat {message, product_id}
    BE->>Orch: route(message, product_id)
    Orch->>Analysis: analyze_reviews(product_id)
    Analysis->>DB: fetch reviews
    DB-->>Analysis: customer_reviews
    Analysis-->>Orch: sentiment summary
    Orch->>Rec: recommend_alternatives(category, min_rating)
    Rec->>DB: query similar products
    DB-->>Rec: alternatives
    Rec-->>Orch: top alternatives
    Orch-->>BE: full response
    BE-->>FE: AI response + alternatives
    FE-->>U: Chat message + product cards
```
