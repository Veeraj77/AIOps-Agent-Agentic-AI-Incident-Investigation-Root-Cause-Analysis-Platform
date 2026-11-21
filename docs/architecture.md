# AIOps Agent – System Architecture

## 1. High-Level Architecture Overview

The **AIOps Agent** is designed around a multi-tier agentic architecture that combines:
1. **High-Speed Deterministic Parsing & Anti-Pattern Recognition** (zero-hallucination baseline)
2. **Local Vector Search RAG** (ChromaDB + Sentence Transformers)
3. **Autonomous Agent Workflow** (LangGraph StateGraph with conditional execution)
4. **LLM Root Cause Synthesis** (Groq / Llama 3)
5. **Strict Schema Validation & Audit Persistence** (Pydantic & SQLite)
6. **Enterprise Dark Observability Console** (React + Vite + Tailwind CSS)

```
       +------------------------------------------------------------------+
       |               React Dashboard (Vite + Tailwind)                  |
       |  [Overview] [New Investigation] [Knowledge Base] [Audit History] |
       +--------------------------------+---------------------------------+
                                        | REST (JSON / Multipart)
                                        v
       +------------------------------------------------------------------+
       |                    FastAPI Backend Core                          |
       |     CORS Middleware | Lifespan Manager | Custom Error Handling   |
       +-------+--------------------+---------------------+---------------+
               |                    |                     |
     POST /incidents/analyze        | POST /documents/upload
               |                    |                     |
               v                    v                     v
       +-------------------+  +---------------+  +------------------------+
       | Ingestion Engine  |  | Chunking &    |  | SQLite Audit Store     |
       |  - Log Normalizer |  | Embeddings    |  |  - investigations      |
       |  - Severity Model |  | (MiniLM-L6-v2)|  |  - documents metadata  |
       +-------------------+  +-------+-------+  +------------------------+
                                      |
                                      v
                             +-----------------+
                             | ChromaDB Vector |
                             | Store (Cosine)  |
                             +--------+--------+
                                      |
                                      | Semantic Retrieval
                                      v
       +------------------------------------------------------------------+
       |                  LangGraph Agent Orchestration                   |
       |                                                                  |
       |  [understand_incident] --> [llm_understand]                      |
       |                                   |                              |
       |                                   +-- (conditional: has errors?) |
       |                                   |                              |
       |                                   v                              |
       |                          [retrieve_docs] (RAG)                   |
       |                                   |                              |
       |                                   v                              |
       |                       [investigate_root_cause]                   |
       |                                   |                              |
       |                                   v                              |
       |                          [generate_report]                       |
       |                                                                  |
       |  * Powered by Groq API (Llama 3 8B / 70B)                        |
       |  * Grounded by Log Citations + KB References                     |
       +------------------------------------------------------------------+
```

---

## 2. Key Components

### A. Ingestion & Pre-Processing
- **`app/ingestion/log_parser.py`**: Accepts raw log blocks or uploaded files. Uses ordered regular expressions to extract timestamps, normalized log levels (CRITICAL, ERROR, WARNING, INFO, DEBUG), service components, and HTTP endpoint paths.
- **`app/ingestion/document_loader.py`**: Extracts text from `.pdf`, `.txt`, and `.md` files.

### B. Analytical Engines
- **`app/analysis/frequency_analyzer.py`**: Computes total line counts, error rates, unique message counts, and ranks top occurring error signatures.
- **`app/analysis/pattern_detector.py`**: Matches incoming log streams against 8 critical infrastructure failure patterns:
  - Database Connection Pool Exhaustion
  - HTTP 5xx Server Errors
  - API Slow Response / Timeout
  - Memory Pressure / Out of Memory
  - Authentication / Authorization Failures
  - Disk / File System Errors
  - Network Connectivity Issues
  - Cascading Failure
- **`app/analysis/severity_classifier.py`**: Combines error counts, error rates, pattern severities, and cascading risks into an objective score (0–100) mapped to `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`.

### C. Local Vector Database & RAG
- **`app/rag/chunking.py`**: Slices document text into overlapping segments (500 chars, 50 chars overlap) to preserve semantic context across chunk boundaries.
- **`app/rag/embeddings.py`**: Uses `sentence-transformers/all-MiniLM-L6-v2` locally on CPU. Fast, zero-cost, no rate limits.
- **`app/rag/vector_store.py`**: Persists embeddings and chunk text in `./storage/chroma_db` using Cosine distance HNSW indexing.
- **`app/rag/retriever.py`**: Formats top-k matching documents into cited context blocks for the LLM.

### D. LangGraph Multi-Node Agent
The agent state is defined as an `AgentState` TypedDict flowing through nodes:
1. **`understand_incident_node`**: Executes deterministic parsing, error counting, pattern detection, and initial severity rating. Sets `should_retrieve` flag.
2. **`llm_understand_node`**: Invokes LLM to construct a human-readable title, non-technical executive summary, technical overview, and observable symptoms.
3. **`retrieve_docs_node`**: Conditional branch. If error telemetry exists, queries ChromaDB with incident signatures to retrieve matching runbook excerpts.
4. **`investigate_root_cause_node`**: The core diagnostic step. Prompt instructs the LLM to hypothesize the probable cause, consider alternative hypotheses, cite direct log lines, and formulate a prioritized remediation plan.
5. **`generate_report_node`**: Finalizes state and marks `is_complete = True`.

### E. Data Contracts & Persistence
- Validated with Pydantic `InvestigationReport` schema.
- Persisted to SQLite via SQLAlchemy ORM in `./storage/aiops.db`.
