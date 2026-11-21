# 🤖 AIOps Agent – Project Status Dashboard

> **Last Updated:** 2026-11-20 20:55 IST (12-Node Multi-Agent Architecture Upgrade Verified)  
> **Current Stage:** 12-NODE MULTI-AGENT ARCHITECTURE & PRODUCTION DEPLOYMENT  
> **Overall Progress:** ██████████ 100% (Upgraded 12-Node Architecture Fully Verified)  
> **Full Test Suite Results:** ✅ 44/44 PASSED (100% in 118.24s)  
> - Agent Node Unit Suite: ✅ 14/14 PASSED (`tests/test_agent_nodes.py`)  
> - Core Backend Suite: ✅ 27/27 PASSED (`tests/test_backend.py`)  
> - Live Groq LLM Tests: ✅ 3/3 PASSED (`tests/test_groq_live.py` via `qwen/qwen3.8-27b`)  
> **Evaluation Benchmark:** ✅ 100.0% Severity Accuracy | 91.11% Pattern F1 | 7.7ms Latency  
> **Frontend Build:** ✅ VITE BUILD PASSED (1654 modules, 0 errors in 6.98s)  
> **Active Host Endpoints:**  
> - Frontend UI: **http://localhost:5173** (ONLINE)  
> - Backend API: **http://localhost:8000/health** (ONLINE)  
> - Interactive Docs: **http://localhost:8000/docs** (ONLINE)  

---

## 🖥️ Environment Snapshot

| Tool | Version | Status |
|------|---------|--------|
| Python | 3.13.7 | ✅ Verified & Operational |
| Node.js | v24.12.0 | ✅ Verified & Operational |
| npm | 10.2.4 | ✅ Dependencies Installed |
| FastAPI | 0.120.0 | ✅ Live on port 8000 |
| React | 18.3.1 | ✅ Production Build Verified |
| Vite | 6.4.6 | ✅ Live on port 5173 |
| LangChain | 1.5.0 | ✅ Verified & Operational |
| LangGraph | 1.2.20 | ✅ 12-Node StateGraph with Conditional Routing |
| ChromaDB | 1.5.9 | ✅ Persistent Cosine Space Ready |
| Sentence Transformers | 6.3.0 | ✅ all-MiniLM-L6-v2 Operational |
| Groq SDK | 0.37.1 | ✅ Live Inference Verified (`qwen/qwen3.8-27b`, max_tokens=800) |
| SQLite | 3 (WAL) | ✅ SQLAlchemy ORM Initialized & Persisted |
| Docker Engine | 29.9.3 | ✅ Running (WSL2 desktop-linux context) |
| Docker Compose | v5.7.0 | ✅ Installed & Operational |

---

## 🏗️ Upgraded 12-Node Multi-Agent Architecture

```mermaid
flowchart TD
    N1["Node 1: Incident Intake Agent"] --> N2["Node 2: Data Validation Agent"]
    
    N2 -- "Invalid / Empty Logs" --> N12["Node 12: Final Response Agent"]
    N2 -- "Valid Submission" --> N3["Node 3: Severity Classification Agent"]
    
    N3 --> N4["Node 4: Log Analysis Agent"]
    
    N4 -- "Logs Clean (should_retrieve = False)" --> N6["Node 6: Pattern Correlation Agent"]
    N4 -- "Errors Detected (should_retrieve = True)" --> N5["Node 5: RAG Retrieval Agent"]
    N5 --> N6
    
    N6 --> N7["Node 7: Root Cause Analysis Agent"]
    N7 --> N8["Node 8: Hypothesis Validation Agent"]
    
    N8 -- "Grounding Incomplete (Retry loop <= 1)" --> N7
    N8 -- "Hypothesis Validated" --> N9["Node 9: Remediation Planning Agent"]
    
    N9 --> N10["Node 10: Report Generation Agent"]
    N10 --> N11["Node 11: Memory & Learning Agent"]
    N11 --> N12
```

### Node Responsibility Breakdown

| Node | Name | Function / Responsibility | Output State Keys |
| :---: | :--- | :--- | :--- |
| **1** | `incident_intake_node` | Accepts raw incident logs, environment, and service metadata; creates UUID and initial timestamps. | `incident_id`, `incident_input`, `intake_timestamp` |
| **2** | `data_validation_node` | Validates log non-emptiness, normalizes strings, and catches malformed inputs early. | `normalized_context`, `is_valid_input`, `validation_errors` |
| **3** | `severity_classification_node` | Deterministically calculates severity (0–100 score) using error counts, cascading risk, and service tier. | `severity`, `severity_score`, `severity_reasoning` |
| **4** | `log_analysis_node` | Parses logs, computes error frequencies, and sets conditional retrieval flag `should_retrieve`. | `log_analysis`, `parsed_entries`, `should_retrieve` |
| **5** | `rag_retrieval_node` | Queries ChromaDB using Sentence Transformers embeddings for matching historical incidents and runbooks. | `retrieved_documents`, `rag_context_text` |
| **6** | `pattern_correlation_node` | Correlates logs with 8 known infrastructure anti-patterns (OOM, DB connection pool, cascading 5xx). | `correlated_patterns`, `matching_anti_patterns` |
| **7** | `root_cause_analysis_node` | Invokes Groq LLM (`qwen/qwen3.8-27b`) with automatic fallback to deterministic reasoning on rate limits. | `root_cause_hypotheses`, `primary_root_cause` |
| **8** | `hypothesis_validation_node` | Cross-references LLM hypotheses with verified log citations; assigns confidence level (HIGH/MED/LOW). | `validated_hypotheses`, `confidence_score`, `evidence_grounding` |
| **9** | `remediation_planning_node` | Synthesizes prioritized immediate mitigation steps and long-term permanent architecture recommendations. | `remediation_plan`, `immediate_actions`, `permanent_fixes` |
| **10** | `report_generation_node` | Builds comprehensive, typed Pydantic `InvestigationReport` model separating facts from AI hypotheses. | `investigation_report`, `executive_summary` |
| **11** | `memory_learning_node` | Persists completed report and full node execution audit trail into SQLite (`storage/aiops.db`). | `memory_persisted`, `memory_record_id` |
| **12** | `final_response_node` | Packages terminal API response payload, computes total execution latency, and marks workflow complete. | `final_response`, `is_complete`, `total_latency_ms` |

### Conditional Routing Rules
- **`_route_validation`:** When `is_valid_input = False`, jumps directly to Node 12 with structured error details, bypassing heavy computation.
- **`_route_retrieval`:** When `should_retrieve = False` (clean logs), skips ChromaDB retrieval (Node 5) directly to Node 6, saving embedding latency.
- **`_route_validation_retry`:** When hypothesis confidence is LOW and ungrounded, loops back from Node 8 to Node 7 for a single refinement cycle (max 1 retry).

---

## 📋 Stage Progress

| Stage | Description | Status | Verification Result |
|-------|-------------|--------|---------------------|
| **Stage 1** | Project structure + Python env + FastAPI setup | ✅ COMPLETED | FastAPI running, CORS configured, Swagger at `/docs` |
| **Stage 2** | Log ingestion, parsing, error detection, frequency analysis, severity classification | ✅ COMPLETED | Multi-format regex parser, 8 anti-patterns, 0–100 scoring |
| **Stage 3** | PDF/TXT document ingestion, chunking, embeddings, ChromaDB | ✅ COMPLETED | Overlapping chunker, Sentence Transformers, ChromaDB upsert |
| **Stage 4** | LLM integration (Groq), LLM service, RAG Q&A | ✅ COMPLETED | Groq API verified with live inference (`qwen/qwen3.8-27b`) |
| **Stage 5** | 12-Node Agentic LangGraph Architecture Upgrade | ✅ COMPLETED | 12 distinct nodes, 3 conditional routing branches, list reducers |
| **Stage 6** | Structured reports (Pydantic), SQLite history | ✅ COMPLETED | Pydantic `InvestigationReport` schema, SQLite persistence |
| **Stage 7** | React dashboard, frontend-backend integration | ✅ COMPLETED | Modern Dark UI (Vite + Tailwind), 12 components, 5 pages |
| **Stage 8** | Evaluation framework, Docker, complete documentation | ✅ COMPLETED | Benchmark suite passing (100% / 91.11%), Docker ready |

---

## 🛡️ Engineering Audit Scorecard

| Audit Area | Rating | Verified Findings |
| :--- | :---: | :--- |
| **1. 12-Node Multi-Agent Graph** | **PASS** | 12 nodes compiled, 3 conditional branches verified, TypedDict state reducers active. |
| **2. Agent Unit Tests** | **PASS** | 14/14 tests passed in `tests/test_agent_nodes.py` (all 12 nodes + routing + graph). |
| **3. Backend Regression** | **PASS** | 27/27 tests passed in `tests/test_backend.py`. Zero regressions on legacy contracts. |
| **4. Live Groq LLM Inference** | **PASS** | 3/3 tests passed in `tests/test_groq_live.py` via `qwen/qwen3.8-27b` with `max_tokens=800`. |
| **5. RAG Pipeline** | **PASS** | Sentence Transformers (`all-MiniLM-L6-v2`) + ChromaDB cosine vector search verified. |
| **6. Evaluation Suite** | **PASS** | 100.0% Severity Accuracy, 91.11% Pattern F1, 7.7ms latency (6/6 passing). |
| **7. Frontend Application** | **PASS** | Vite production build passed (1654 modules, 0 errors); dev server live on port 5173. |
| **8. Security & Secrets** | **PASS** | `.env` gitignored, zero committed credentials, CORS restricted to localhost. |
| **9. Database Persistence** | **PASS** | SQLite WAL mode operational; reports persisted and retrieved cleanly. |

---

## ✅ Test Execution Proof

### 1. Full 44-Test Backend Suite (`python -m pytest tests/ -v`)
```
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\AI_project\AIOps-Agent\backend
collected 44 items

tests/test_agent_nodes.py::test_node1_incident_intake PASSED             [  2%]
tests/test_agent_nodes.py::test_node2_data_validation_success PASSED     [  4%]
tests/test_agent_nodes.py::test_node2_data_validation_rejection PASSED   [  6%]
tests/test_agent_nodes.py::test_node3_severity_classification PASSED     [  9%]
tests/test_agent_nodes.py::test_node4_log_analysis PASSED                [ 11%]
tests/test_agent_nodes.py::test_node5_rag_retrieval_graceful PASSED      [ 13%]
tests/test_agent_nodes.py::test_node6_pattern_correlation PASSED         [ 15%]
tests/test_agent_nodes.py::test_node7_root_cause_analysis PASSED         [ 18%]
tests/test_agent_nodes.py::test_node8_hypothesis_validation PASSED       [ 20%]
tests/test_agent_nodes.py::test_node9_remediation_planning PASSED        [ 22%]
tests/test_agent_nodes.py::test_node10_report_generation PASSED          [ 25%]
tests/test_agent_nodes.py::test_node11_memory_learning PASSED            [ 27%]
tests/test_agent_nodes.py::test_node12_final_response PASSED             [ 29%]
tests/test_agent_nodes.py::test_full_12_node_graph_execution PASSED      [ 31%]
tests/test_backend.py::TestLogParser::test_parse_basic_error_logs PASSED [ 34%]
tests/test_backend.py::TestLogParser::test_parse_timestamped_logs PASSED [ 36%]
tests/test_backend.py::TestLogParser::test_parse_empty_raises PASSED     [ 38%]
tests/test_backend.py::TestLogParser::test_parse_whitespace_only_raises PASSED [ 40%]
tests/test_backend.py::TestLogParser::test_parse_multiple_formats PASSED [ 43%]
tests/test_backend.py::TestLogParser::test_endpoint_extraction PASSED    [ 45%]
tests/test_backend.py::TestLogParser::test_severity_weight_ordering PASSED [ 47%]
tests/test_backend.py::TestFrequencyAnalyzer::test_frequency_counts_errors PASSED [ 50%]
tests/test_backend.py::TestFrequencyAnalyzer::test_error_rate_calculation PASSED [ 52%]
tests/test_backend.py::TestFrequencyAnalyzer::test_top_errors_sorted PASSED [ 54%]
tests/test_backend.py::TestFrequencyAnalyzer::test_empty_entries_returns_empty_report PASSED [ 56%]
tests/test_backend.py::TestPatternDetector::test_detect_db_exhaustion PASSED [ 59%]
tests/test_backend.py::TestPatternDetector::test_detect_http_5xx PASSED  [ 61%]
tests/test_backend.py::TestPatternDetector::test_clean_logs_no_patterns PASSED [ 63%]
tests/test_backend.py::TestPatternDetector::test_patterns_sorted_by_severity PASSED [ 65%]
tests/test_backend.py::TestSeverityClassifier::test_critical_logs_get_high_severity PASSED [ 68%]
tests/test_backend.py::TestSeverityClassifier::test_info_only_logs_get_low_severity PASSED [ 70%]
tests/test_backend.py::TestSeverityClassifier::test_severity_result_has_reasoning PASSED [ 72%]
tests/test_backend.py::TestAPIEndpoints::test_health_endpoint PASSED     [ 75%]
tests/test_backend.py::TestRootEndpoint::test_root_endpoint PASSED        [ 77%]
tests/test_backend.py::TestAPIEndpoints::test_analyze_incident_success PASSED [ 79%]
tests/test_backend.py::TestAPIEndpoints::test_analyze_incident_empty_logs_returns_422 PASSED [ 81%]
tests/test_backend.py::TestAPIEndpoints::test_analyze_incident_whitespace_returns_error PASSED [ 84%]
tests/test_backend.py::TestAPIEndpoints::test_list_investigations_returns_list PASSED [ 86%]
tests/test_backend.py::TestAPIEndpoints::test_get_nonexistent_investigation_returns_404 PASSED [ 88%]
tests/test_backend.py::TestAPIEndpoints::test_list_documents_returns_list PASSED [ 90%]
tests/test_backend.py::TestAPIEndpoints::test_document_stats_endpoint PASSED [ 93%]
tests/test_groq_live.py::test_groq_settings_and_no_hardcoded_key PASSED  [ 95%]
tests/test_groq_live.py::test_groq_live_connectivity PASSED              [ 97%]
tests/test_groq_live.py::test_groq_langchain_chat_model_invocation PASSED [100%]

============================= 44 passed in 118.24s =============================
```

### 2. Benchmark Evaluation Suite (`python evaluation/evaluate.py`)
```
================================================================================
 🔬 AIOPS AGENT – BENCHMARK EVALUATION SUITE
================================================================================
 Loaded 6 test cases from evaluation/test_cases.json

 ✅ [TC-01] Database Connection Pool Exhaustion      Sev: HIGH     (Exp: HIGH) | F1: 0.80 | Latency: 36.8ms
 ✅ [TC-02] Authentication and JWT Failure           Sev: CRITICAL (Exp: CRITICAL) | F1: 1.00 | Latency: 2.5ms
 ⚠️ [TC-03] HTTP 500 Internal Server Cascading Errors Sev: HIGH     (Exp: HIGH) | F1: 0.67 | Latency: 2.2ms
 ✅ [TC-04] API Latency and Timeout Degradation      Sev: MEDIUM   (Exp: MEDIUM) | F1: 1.00 | Latency: 1.8ms
 ✅ [TC-05] Java Heap Space Out of Memory            Sev: CRITICAL (Exp: CRITICAL) | F1: 1.00 | Latency: 1.4ms
 ✅ [TC-06] Healthy Application Normal Operations    Sev: INFO     (Exp: INFO) | F1: 1.00 | Latency: 1.5ms

--------------------------------------------------------------------------------
 📊 AGGREGATE PERFORMANCE SUMMARY
--------------------------------------------------------------------------------
 • Average Severity Accuracy:      100.0%
 • Average Pattern Detection F1:   91.11%
 • Average Deterministic Latency:  7.7 ms
 • Test Cases Evaluated:           6/6 passed schema validation
================================================================================
```

### 3. Live End-to-End Investigation Run (`POST /api/investigations/run`)
```
HTTP Status: 200 OK
Investigation ID: 06969f93-645a-401a-b429-79d9de6b2540
Severity: MEDIUM
Root Cause: [HYPOTHESIS] Database Connection Pool Exhausted detected based on recurring telemetry error signatures.
Confidence: HIGH
Remediation Count: 2 actionable steps
Symptoms:
 - DB connection pool exhausted (Active: 100/100)
 - Timeout waiting for idle connection after 30000ms
 - Slow query detected on table orders (duration=45000ms)
 - HTTP 500 Internal Server Error returned to checkout client
Persistence Check: Successfully saved to SQLite and verified via GET /api/investigations
```

---

## 📁 Complete Repository File Inventory

```
d:\AI_project\
├── STATUS.md                                        ✅ Live Status Dashboard (Root)
├── README.md                                        ✅ Project Overview
│
└── AIOps-Agent/
    ├── STATUS.md                                    ✅ Synchronized Status Dashboard (Repo)
    ├── FINAL_ENGINEERING_AUDIT.md                   ✅ Final Verification, Audit & Production Readiness
    ├── VERIFICATION_RESULTS.md                      ✅ Execution Log & Raw Terminal Outputs
    ├── REMAINING_TASKS.md                           ✅ Prioritized Action Items
    ├── FINAL_AUDIT.md                               ✅ Architectural Audit Report
    ├── Dockerfile                                   ✅ Backend Containerfile (CPU-optimized)
    ├── docker-compose.yml                           ✅ Multi-service compose
    ├── .gitignore                                   ✅ Comprehensive exclusion rules
    ├── README.md                                    ✅ Full Engineering Documentation
    │
    ├── backend/
    │   ├── .env                                     ✅ Environment variables (GROQ_API_KEY)
    │   ├── .env.example                             ✅ Sanitized template
    │   ├── requirements.txt                         ✅ Backend dependencies (langchain-core>=0.3.29)
    │   ├── Dockerfile                               ✅ Container build
    │   │
    │   ├── app/
    │   │   ├── main.py                              ✅ FastAPI app entry, CORS & lifespan
    │   │   ├── config.py                            ✅ Pydantic BaseSettings (llm_max_tokens=800)
    │   │   │
    │   │   ├── api/routes/
    │   │   │   ├── health.py                        ✅ GET /health
    │   │   │   ├── incidents.py                     ✅ POST /api/incidents/analyze, upload
    │   │   │   ├── documents.py                     ✅ POST /api/documents/upload, stats
    │   │   │   └── investigations.py                ✅ POST /api/investigations/run, list, get
    │   │   │
    │   │   ├── core/
    │   │   │   ├── logging.py                       ✅ structlog JSON/console logging
    │   │   │   └── exceptions.py                    ✅ Custom HTTP exceptions
    │   │   │
    │   │   ├── ingestion/
    │   │   │   ├── log_parser.py                    ✅ Multi-format regex parser
    │   │   │   └── document_loader.py               ✅ PDF (pypdf) & TXT loader
    │   │   │
    │   │   ├── analysis/
    │   │   │   ├── frequency_analyzer.py            ✅ Line counts, error rates, top-N
    │   │   │   ├── pattern_detector.py              ✅ 8 infrastructure anti-patterns
    │   │   │   └── severity_classifier.py           ✅ Weighted scoring model (0–100)
    │   │   │
    │   │   ├── rag/
    │   │   │   ├── chunking.py                      ✅ Overlapping text chunker
    │   │   │   ├── embeddings.py                    ✅ Sentence Transformers (cached)
    │   │   │   ├── vector_store.py                  ✅ ChromaDB cosine vector storage
    │   │   │   └── retriever.py                     ✅ Semantic search & formatting
    │   │   │
    │   │   ├── agents/
    │   │   │   ├── state.py                         ✅ TypedDict AgentState with list reducers
    │   │   │   ├── prompts.py                       ✅ Structured prompts for reasoning
    │   │   │   ├── tools.py                         ✅ LangChain-compatible tools
    │   │   │   ├── nodes.py                         ✅ 12 distinct agent nodes + legacy wrappers
    │   │   │   └── graph.py                         ✅ 12-node StateGraph with conditional routing
    │   │   │
    │   │   ├── schemas/
    │   │   │   ├── incident.py                      ✅ Pydantic incident contracts
    │   │   │   └── report.py                        ✅ Pydantic InvestigationReport schema
    │   │   │
    │   │   ├── services/
    │   │   │   ├── llm_service.py                   ✅ ChatGroq client (max_tokens=800)
    │   │   │   └── investigation_service.py         ✅ 12-node executor & SQLite storage
    │   │   │
    │   │   └── database/
    │   │       └── connection.py                    ✅ SQLAlchemy models & get_db_context()
    │   │
    │   ├── storage/
    │   │   └── aiops.db                             ✅ SQLite persistence database
    │   │
    │   └── tests/
    │       ├── test_agent_nodes.py                  ✅ 14 Pytest test cases (12 nodes + routing)
    │       ├── test_backend.py                      ✅ 27 Pytest test cases (all passing)
    │       └── test_groq_live.py                    ✅ 3 Pytest test cases (live inference)
    │
    ├── frontend/
    │   ├── package.json                             ✅ React 18, Vite, Tailwind, Lucide
    │   ├── vite.config.js                           ✅ Vite configuration
    │   ├── tailwind.config.js                       ✅ Tailwind dark theme
    │   ├── postcss.config.js                        ✅ PostCSS plugins
    │   ├── nginx.conf                               ✅ Production Nginx reverse proxy
    │   ├── Dockerfile                               ✅ Multi-stage Node->Nginx build
    │   ├── index.html                               ✅ HTML5 entry
    │   ├── .env                                     ✅ VITE_API_BASE_URL=http://localhost:8000
    │   ├── .env.example                             ✅ Frontend env template
    │   │
    │   └── src/
    │       ├── main.jsx                             ✅ React DOM root
    │       ├── App.jsx                              ✅ Main navigation & polling
    │       ├── index.css                            ✅ Tailwind directives & custom scrollbars
    │       │
    │       ├── services/
    │       │   └── api.js                           ✅ Centralized Axios client (9 endpoints)
    │       │
    │       ├── components/
    │       │   ├── Sidebar.jsx                      ✅ Navigation sidebar with status pill
    │       │   ├── Header.jsx                       ✅ Top bar with LLM model chips
    │       │   ├── StatCard.jsx                     ✅ Metrics card with color themes
    │       │   ├── SeverityBadge.jsx                ✅ Severity pills (CRITICAL to INFO)
    │       │   ├── LogUploader.jsx                  ✅ Input textarea, file upload, sample loaders
    │       │   ├── DocumentUploader.jsx             ✅ Runbook drag-and-drop ingestion
    │       │   ├── IncidentSummary.jsx              ✅ Rule-based deterministic results card
    │       │   ├── RootCauseCard.jsx                ✅ AI hypothesis & confidence badge
    │       │   ├── EvidencePanel.jsx                ✅ Log citations & RAG doc references
    │       │   ├── RemediationPanel.jsx             ✅ Immediate actions & prioritized plan
    │       │   ├── InvestigationReport.jsx          ✅ Full synthesized report view
    │       │   ├── LoadingState.jsx                 ✅ Animated agent progress indicator
    │       │   └── ErrorMessage.jsx                 ✅ Retryable error notification
    │       │
    │       └── pages/
    │           ├── Dashboard.jsx                    ✅ Telemetry stats, recent incidents
    │           ├── Investigation.jsx                ✅ New investigation & RCA viewer
    │           ├── KnowledgeBase.jsx                ✅ ChromaDB runbook manager
    │           ├── History.jsx                      ✅ Searchable historical audit trail
    │           └── SystemStatus.jsx                 ✅ Live component health probes
    │
    ├── data/sample_logs/
    │   ├── database_incident.log                    ✅ Database pool timeout sample
    │   └── auth_incident.log                        ✅ JWT authentication failure sample
    │
    ├── evaluation/
    │   ├── test_cases.json                          ✅ 6 benchmark failure scenarios
    │   ├── metrics.py                               ✅ Scoring algorithms (F1, accuracy, latency)
    │   ├── evaluate.py                              ✅ Automated evaluation runner
    │   └── evaluation_report.json                   ✅ Measured benchmark results
    │
    └── docs/
        ├── architecture.md                          ✅ System architecture deep dive
        ├── api_documentation.md                     ✅ Complete REST API contracts
        ├── technical_decisions.md                   ✅ Engineering trade-offs & rationale
        └── audits/
            ├── FINAL_AUDIT.md                       ✅ Historical audit record
            ├── FINAL_ENGINEERING_AUDIT.md           ✅ Master 12-node engineering audit
            ├── REMAINING_TASKS.md                   ✅ Remaining action items
            └── VERIFICATION_RESULTS.md              ✅ Raw verification logs
```

---

## 🚀 How to Run the Platform

### 1. Terminal 1 – Start Backend
```powershell
cd d:\AI_project\AIOps-Agent\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive Swagger API Docs: **`http://localhost:8000/docs`**

### 2. Terminal 2 – Start React Frontend
```powershell
cd d:\AI_project\AIOps-Agent\frontend
npm run dev
```
Open Dashboard: **`http://localhost:5173`**
