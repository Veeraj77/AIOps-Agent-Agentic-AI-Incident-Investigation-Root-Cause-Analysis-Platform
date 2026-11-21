# AIOps Agent – Architectural Decisions & Trade-Offs

This document records the technical rationale, architectural decisions, and trade-offs made during the engineering of the AIOps Agent platform.

---

## 1. Why FastAPI?
- **Asynchronous Performance:** Native ASGI support with Starlette and Uvicorn provides high throughput for concurrent telemetry uploads.
- **Pydantic Data Contracts:** Automatic request validation and schema generation eliminates boilerplate serialization code.
- **Self-Documenting:** Interactive Swagger (`/docs`) and ReDoc (`/redoc`) OpenAPI endpoints facilitate rapid frontend integration.

## 2. Why Groq API as Primary LLM Provider?
- **Inference Speed:** Groq's custom LPU (Language Processing Unit) delivers 300–500 tokens/second on open-weight models (Llama 3 8B / 70B), reducing investigation wait time from ~30s to under 3s.
- **Cost Accessibility:** Generous free-tier quotas make it ideal for portfolio demonstration, evaluation, and interview walkthroughs.
- **Decoupled Service Interface:** The `llm_service.py` layer isolates provider calls so alternate providers (OpenAI, Anthropic, local Ollama) can be swapped via configuration without touching agent nodes.

## 3. Why Sentence Transformers (`all-MiniLM-L6-v2`) for Embeddings?
- **Zero API Dependency:** Generating embeddings locally avoids per-chunk API costs, network latency, and third-party rate limits.
- **Compact & Efficient:** The 384-dimensional vector representation balances high semantic precision with minimal RAM usage (~120MB memory footprint).
- **Fast Startup:** Cached via `@lru_cache` so the model loads once into memory and stays warm.

## 4. Why ChromaDB for Vector Storage?
- **In-Process & Persistent:** Can run embedded in Python without requiring a dedicated cluster (like Milvus or Pinecone).
- **Disk Persistence:** Embeddings survive server reboots in `./storage/chroma_db`.
- **HNSW Indexing:** Native cosine distance calculation provides sub-millisecond nearest-neighbor search.

## 5. Why LangGraph over Linear Chains?
- **Explicit State Management:** TypedDict `AgentState` acts as a strongly-typed whiteboard where each node reads previous findings and appends new diagnostics.
- **Conditional Branching:** The workflow dynamically skips RAG vector queries when telemetry contains no errors, conserving compute and token budget.
- **Fault Tolerance:** If LLM inference fails (network hiccup, rate limit), node fallbacks gracefully construct a partial diagnostic report without crashing the server.

## 6. Why SQLite for Audit Persistence?
- **Zero Infrastructure Burden:** Single file `./storage/aiops.db` requires zero configuration, daemon processes, or cloud credentials.
- **SQLAlchemy ORM Portability:** Models can be migrated to PostgreSQL or MySQL by modifying a single `DATABASE_URL` environment string.
- **Audit Traceability:** Preserves full incident JSON reports, timestamps, original logs, and affected service tags.

## 7. Known Limitations & Trade-Offs
1. **Log Context Windows:** Very large log dumps (>500KB) are parsed deterministically, but prompts truncate log samples to ~3000 characters to respect LLM context budgets.
2. **Cold Start Latency:** First-time ChromaDB / Sentence Transformer queries take ~5-10s to warm up PyTorch weights into memory; subsequent queries run in milliseconds.
3. **Single-Node Deployment:** Current design targets local workstation development and Docker single-node deployments. For distributed multi-tenant workloads, Celery queues and Redis task caching would be added.
