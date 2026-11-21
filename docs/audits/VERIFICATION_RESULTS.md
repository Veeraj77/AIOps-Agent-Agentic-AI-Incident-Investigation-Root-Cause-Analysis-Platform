# 📋 AIOps Agent – Verification Results Log

> **Execution Date:** 2026-11-15 01:05 IST  
> **Auditor Role:** Senior AI Engineer & Independent QA Lead  
> **Environment:** Windows 11, Python 3.13.7, Node.js 24.12.0, Vite 6.4.6  

---

## 1. Backend Pytest Execution

**Command:**
```powershell
cd d:\AI_project\AIOps-Agent\backend
python -m pytest tests/test_backend.py -v --tb=short
```

**Actual Terminal Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0 -- C:\Python313\python.exe
cachedir: .pytest_cache
rootdir: D:\AI_project\AIOps-Agent\backend
plugins: anyio-4.11.0, hydra-core-1.3.8, langsmith-0.14.17
collecting ... collected 27 items

tests/test_backend.py::TestLogParser::test_parse_basic_error_logs PASSED [  3%]
tests/test_backend.py::TestLogParser::test_parse_timestamped_logs PASSED [  7%]
tests/test_backend.py::TestLogParser::test_parse_empty_raises PASSED     [ 11%]
tests/test_backend.py::TestLogParser::test_parse_whitespace_only_raises PASSED [ 14%]
tests/test_backend.py::TestLogParser::test_parse_multiple_formats PASSED [ 18%]
tests/test_backend.py::TestLogParser::test_endpoint_extraction PASSED    [ 22%]
tests/test_backend.py::TestLogParser::test_severity_weight_ordering PASSED [ 25%]
tests/test_backend.py::TestFrequencyAnalyzer::test_frequency_counts_errors PASSED [ 29%]
tests/test_backend.py::TestFrequencyAnalyzer::test_error_rate_calculation PASSED [ 33%]
tests/test_backend.py::TestFrequencyAnalyzer::test_top_errors_sorted PASSED [ 37%]
tests/test_backend.py::TestFrequencyAnalyzer::test_empty_entries_returns_empty_report PASSED [ 40%]
tests/test_backend.py::TestPatternDetector::test_detect_db_exhaustion PASSED [ 44%]
tests/test_backend.py::TestPatternDetector::test_detect_http_5xx PASSED  [ 48%]
tests/test_backend.py::TestPatternDetector::test_clean_logs_no_patterns PASSED [ 51%]
tests/test_backend.py::TestPatternDetector::test_patterns_sorted_by_severity PASSED [ 55%]
tests/test_backend.py::TestSeverityClassifier::test_critical_logs_get_high_severity PASSED [ 59%]
tests/test_backend.py::TestSeverityClassifier::test_info_only_logs_get_low_severity PASSED [ 62%]
tests/test_backend.py::TestSeverityClassifier::test_severity_result_has_reasoning PASSED [ 66%]
tests/test_backend.py::TestAPIEndpoints::test_health_endpoint PASSED     [ 70%]
tests/test_backend.py::TestAPIEndpoints::test_root_endpoint PASSED       [ 74%]
tests/test_backend.py::TestAPIEndpoints::test_analyze_incident_success PASSED [ 77%]
tests/test_backend.py::TestAPIEndpoints::test_analyze_incident_empty_logs_returns_422 PASSED [ 81%]
tests/test_backend.py::TestAPIEndpoints::test_analyze_incident_whitespace_returns_error PASSED [ 85%]
tests/test_backend.py::TestAPIEndpoints::test_list_investigations_returns_list PASSED [ 88%]
tests/test_backend.py::TestAPIEndpoints::test_get_nonexistent_investigation_returns_404 PASSED [ 92%]
tests/test_backend.py::TestAPIEndpoints::test_list_documents_returns_list PASSED [ 96%]
tests/test_backend.py::TestAPIEndpoints::test_document_stats_endpoint PASSED [100%]

============================= 27 passed in 11.21s =============================
```

---

## 2. Benchmark Evaluation Suite Execution

**Command:**
```powershell
cd d:\AI_project\AIOps-Agent
python evaluation/evaluate.py
```

**Actual Terminal Output:**
```
================================================================================
 🔬 AIOPS AGENT – BENCHMARK EVALUATION SUITE
================================================================================
 Loaded 6 test cases from D:\AI_project\AIOps-Agent\evaluation\test_cases.json

 ✅ [TC-01] Database Connection Pool Exhaustion      Sev: HIGH     (Exp: HIGH) | F1: 0.80 | Latency: 34.1ms
 ✅ [TC-02] Authentication and JWT Failure           Sev: CRITICAL (Exp: CRITICAL) | F1: 1.00 | Latency: 1.4ms
 ⚠️ [TC-03] HTTP 500 Internal Server Cascading Errors Sev: HIGH     (Exp: HIGH) | F1: 0.67 | Latency: 1.1ms
 ✅ [TC-04] API Latency and Timeout Degradation      Sev: MEDIUM   (Exp: MEDIUM) | F1: 1.00 | Latency: 1.2ms
 ✅ [TC-05] Java Heap Space Out of Memory            Sev: CRITICAL (Exp: CRITICAL) | F1: 1.00 | Latency: 1.2ms
 ✅ [TC-06] Healthy Application Normal Operations    Sev: INFO     (Exp: INFO) | F1: 1.00 | Latency: 1.0ms

--------------------------------------------------------------------------------
 📊 AGGREGATE PERFORMANCE SUMMARY
--------------------------------------------------------------------------------
 • Average Severity Accuracy:      100.0%
 • Average Pattern Detection F1:   91.11%
 • Average Deterministic Latency:  6.67 ms
 • Test Cases Evaluated:           6/6 passed schema validation
================================================================================
```

---

## 3. Frontend Production Build

**Command:**
```powershell
cd d:\AI_project\AIOps-Agent\frontend
npm run build
```

**Actual Terminal Output:**
```
> aiops-agent-frontend@1.0.0 build
> vite build

vite v6.4.6 building for production...
transforming...
✓ 1654 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.75 kB │ gzip:  0.49 kB
dist/assets/index-BAGG3gaI.css   25.10 kB │ gzip:  5.28 kB
dist/assets/index-DuYgAQto.js   280.48 kB │ gzip: 85.46 kB
✓ built in 32.05s
```

---

## 4. Docker CLI Verification

**Command:**
```powershell
docker --version
docker info
```

**Actual Terminal Output:**
```
docker : The term 'docker' is not recognized as the name of a cmdlet, function, script file, or operable program. 
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
```
*Result:* Docker runtime is absent from the host system.

---

## 5. Groq LLM Key Check

**Command:**
```powershell
cd d:\AI_project\AIOps-Agent
python -c "from backend.app.config import get_settings; s = get_settings(); print('KEY_CONFIGURED:', bool(s.groq_api_key and s.groq_api_key != 'your_groq_api_key_here'))"
```

**Actual Terminal Output:**
```
KEY_CONFIGURED: False
```
*Result:* Placeholder key `your_groq_api_key_here` present in `backend/.env`.

---

## 6. Real End-to-End Incident Investigation Test

**Incident Test Input:**
```
2026-11-15 10:00:01 ERROR Database connection pool exhausted
2026-11-15 10:00:02 ERROR Failed to acquire database connection
2026-11-15 10:00:03 ERROR HTTP 500 Internal Server Error
2026-11-15 10:00:04 ERROR Request timeout after 30000ms
2026-11-15 10:00:05 CRITICAL Database unavailable
```

**Actual Execution Telemetry:**
- `understand_incident_node`: 5 parsed entries, 4 errors, 1 critical, score 105 -> `CRITICAL`.
- `llm_understand_node`: Handled missing key gracefully; populated fallback title & technical summary.
- `retrieve_docs_node`: Semantic search against ChromaDB queried with incident patterns; retrieved 2 matching chunks from `database_runbook.md` (relevance: 0.4407 and 0.3066).
- `investigate_root_cause_node`: Extracted fallback evidence (3 citations) and generated 3 prioritized remediation steps based on matched pattern diagnostics.
- `generate_report_node`: Validated `InvestigationReport` Pydantic model.
- SQLite Storage: Successfully inserted record into `investigations` table (`id: 5bb2465f-57d8-4084-9743-cef2057a69fe`).
- SQLite Retrieval: Verified retrieval and full deserialization via `get_investigation_by_id`.
