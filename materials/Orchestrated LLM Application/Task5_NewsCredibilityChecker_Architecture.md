# Task 5 · Multi-Source News Credibility Checker

---

## Current Architecture (step1_eval)

The implemented architecture at the current stage. Two-agent structure.

```mermaid
flowchart TD
    Input([Claim]) --> DecompAgent

    subgraph AGENTS["AGENTS  ·  LLM-powered reasoning"]
        DecompAgent["📝 Claim Decomposer</br>─────────────────</br>· Parse entities & domain</br>· Generate 3 targeted queries</br>  (support / deny / expert)"]

        CheckAgent["🔍 Credibility Checker</br>─────────────────</br>· Search with ALL given queries</br>· Compare sources</br>· Assign score + label</br>· Extract contradictions"]
    end

    subgraph TOOLS["TOOLS  ·  No LLM"]
        WebSearch[("🌐 Web Search</br>gpt-4o web_search_preview")]
    end

    subgraph EVAL["PIPELINE EVALUATION (B)"]
        TestCases[("📋 Test Cases</br>4 claims with known labels")]
        EvalFn["evaluate_pipeline()</br>· label match</br>· score in expected range</br>· overall accuracy"]
    end

    DecompAgent -->|"domain + search_queries"| CheckAgent
    CheckAgent <-->|"targeted search"| WebSearch
    CheckAgent --> Output(["📄 Score + Label + Sources + Contradictions"])

    TestCases --> EvalFn
    EvalFn -.->|"runs pipeline per case"| DecompAgent
```

### Current limitations

| Not yet implemented | Impact |
| ------------------- | ------ |
| Source Scoring | All sources have equal weight |
| Reputation Agent | Author and outlet reliability not considered |
| Contradiction Agent | Contradiction detection is shallow, embedded in Checker |
| Critique Loop | No re-search even when evidence is weak |
| RAG / Source Registry | No historical calibration |

---

## Target Architecture (Full Multi-Agent)

The ideal architecture to work toward. Seven agents + four tools.

```mermaid
flowchart TD
    Input([Claim + Accuracy Tier]) --> MetaAgent

    subgraph AGENTS["AGENTS  ·  LLM-powered reasoning"]
        MetaAgent["🧠 Meta Agent</br>─────────────────</br>Orchestrates full flow</br>Decides next step</br>Manages cost budget"]

        DecompAgent["📝 Claim Decomposer Agent</br>─────────────────</br>· Extract entities, dates, numbers</br>· Classify topic domain</br>· Generate search queries"]

        SourceAgent["🗂️ Source Selection Agent</br>─────────────────</br>· Match topic → source pool</br>· Ensure bias & type diversity</br>· Rank by historical reliability"]

        FilterAgent["🔍 Filter Agent</br>─────────────────</br>· Score article relevance</br>· Remove off-topic results</br>· Flag low-quality signals"]

        RepAgent["⭐ Reputation Agent</br>─────────────────</br>· Author track record</br>· Outlet reliability per topic</br>· Conflict-of-interest detection"]

        ContraAgent["⚡ Contradiction Agent</br>─────────────────</br>· Build claim × source matrix</br>· Identify agreements / disputes</br>· Label contradiction severity"]

        CritiqueAgent["🔄 Critique Agent</br>─────────────────</br>· Challenge weak sub-claims</br>· Generate targeted follow-ups</br>· Decide: resolved or loop again"]

        ScoreAgent["📊 Scoring Agent</br>─────────────────</br>· Weighted composite score</br>· Calibrate with historical prior</br>· Produce label + explanation"]
    end

    subgraph TOOLS["TOOLS  ·  Utility functions, no LLM"]
        WebSearch[("🌐 Web Search Tool</br>Tavily / Bing API")]
        RAGTool[("📚 RAG Tool</br>Vector DB  read + write")]
        SrcRegistry[("📋 Source Registry</br>topic → source metadata</br>bias / type / region")]
        PreFilterTool[("⚙️ Pre-filter Tool</br>blacklist · date window</br>duplicate removal")]
    end

    MetaAgent -->|"① decompose claim"| DecompAgent
    DecompAgent -->|"topic tag + parsed claim</br>+ search queries"| MetaAgent

    MetaAgent -->|"② select sources"| SourceAgent
    SourceAgent <-->|"topic lookup"| SrcRegistry
    SourceAgent <-->|"past reliability scores"| RAGTool
    SourceAgent -->|"ranked candidate list"| MetaAgent

    MetaAgent -->|"③ search"| WebSearch
    WebSearch -->|"raw results"| PreFilterTool
    PreFilterTool -->|"rule-filtered articles"| FilterAgent
    FilterAgent -->|"relevance-scored articles"| MetaAgent

    MetaAgent -->|"④ reputation check"| RepAgent
    RepAgent <-->|"author + outlet history"| RAGTool
    RepAgent -->|"per-article weight modifier"| MetaAgent

    MetaAgent -->|"⑤ compare sources"| ContraAgent
    ContraAgent -->|"claim matrix + severity labels"| MetaAgent

    MetaAgent -->|"⑥ critique"| CritiqueAgent
    CritiqueAgent -->|"follow-up queries"| WebSearch
    CritiqueAgent -->|"resolved / unresolved</br>max 2 iterations"| MetaAgent

    MetaAgent -->|"⑦ score"| ScoreAgent
    ScoreAgent <-->|"historical prior"| RAGTool
    ScoreAgent -->|"final score + explanation"| MetaAgent

    MetaAgent -->|"write result back"| RAGTool
    MetaAgent --> Output(["📄 Report + Credibility Score"])
```

---

## Separation of Concerns

| Type | Component | Role | Status |
| ---- | --------- | ---- | ------ |
| **Agent** | Meta Agent | Full orchestration, cost management, next-step decision | Not implemented |
| **Agent** | Claim Decomposer | Claim understanding, topic classification, query generation | ✅ step1_eval |
| **Agent** | Source Selection | Select sources per topic, ensure diversity | Not implemented |
| **Agent** | Filter Agent | LLM-level relevance scoring | Not implemented |
| **Agent** | Reputation Agent | Evaluate author and outlet reliability history | Not implemented |
| **Agent** | Contradiction Agent | Cross-source comparison, contradiction severity labeling | Not implemented |
| **Agent** | Critique Agent | Challenge weak claims, drive re-search loop | Not implemented |
| **Agent** | Scoring Agent | Final score aggregation, historical calibration | Not implemented |
| **Tool** | Web Search Tool | External API call (returns raw data only) | ✅ step1_eval (web_search_preview) |
| **Tool** | Pre-filter Tool | Rule-based filter (blacklist, date window, deduplication) | Not implemented |
| **Tool** | RAG Tool | Vector DB read/write (historical memory) | Not implemented |
| **Tool** | Source Registry | Topic → source metadata, static/semi-static config | Not implemented |

---

## Key Design Principles

### Agents vs Tools

- Tools never reason — pure I/O functions
- Agents never call APIs directly — always go through a Tool
- Meta Agent owns flow control — individual Agents only return results

### Role of RAG

Source Selection, Reputation, and Scoring Agents all reference historical memory.
Past scores, per-source reliability, and known contradiction patterns are used for calibration.

### Critique Loop

The Critique Agent is the only Agent that can trigger a re-search loop.
Cuts off at max 2 iterations or cost limit reached, marking the result as `UNRESOLVED`.

---

## Implementation Roadmap

```text
✅ minimal_mvp   — single agent, 1 LLM call
✅ step1_eval    — Claim Decomposition + Pipeline Evaluation
⬜ step2         — Source Scoring (individual score per source)
⬜ step3         — Contradiction Detection (cross-source comparison)
⬜ step4         — Scoring Agent (weighted composite)
⬜ full          — Meta Agent + all components integrated
```

---

## Open Questions

- [ ] RAG backend: ChromaDB (local) vs Pinecone (managed)
- [ ] Reputation data source: internal DB vs Media Bias/Fact Check API vs skip?
- [ ] Source Registry update frequency: static config vs LLM-driven periodic updates?
- [ ] Critique Loop trigger: always / low-confidence only / user choice?
- [ ] Cost management granularity: token limit / time limit / per-claim budget?
