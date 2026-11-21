# AIOps Agent – REST API Contracts & Documentation

This document defines the complete API contracts for the AIOps Agent backend service.

Base URL: `http://localhost:8000`  
Interactive OpenAPI Explorer: `http://localhost:8000/docs` (Swagger UI)  
Alternative Documentation: `http://localhost:8000/redoc`

---

## 1. System Health & Metadata

### `GET /health`
Returns runtime status and AI configuration.

**Request:** None

**Response `200 OK`:**
```json
{
  "status": "healthy",
  "app_name": "AIOps Agent",
  "version": "1.0.0",
  "llm_provider": "groq",
  "llm_model": "llama3-8b-8192"
}
```

---

## 2. Incident Log Analysis

### `POST /api/incidents/analyze`
Executes deterministic, rule-based log analysis without calling external LLMs. Identifies failure signatures, error frequencies, and severity ratings.

**Request Body:**
```json
{
  "logs": "2024-01-15 10:30:30 ERROR DatabaseService - Connection pool exhausted.\n2024-01-15 10:30:31 ERROR HTTP 500 - /api/orders - Internal Server Error"
}
```

**Response `200 OK`:**
```json
{
  "success": true,
  "total_log_entries": 2,
  "level_counts": {
    "ERROR": 2
  },
  "error_rate_percent": 100.0,
  "unique_error_count": 2,
  "top_errors": [
    {
      "message": "DatabaseService - Connection pool exhausted.",
      "count": 1,
      "percentage": 50.0
    },
    {
      "message": "HTTP 500 - /api/orders - Internal Server Error",
      "count": 1,
      "percentage": 50.0
    }
  ],
  "top_warnings": [],
  "detected_patterns": [
    {
      "pattern_id": "DB_CONNECTION_EXHAUSTION",
      "name": "Database Connection Pool Exhausted",
      "description": "Database connection pool has been exhausted. Requests cannot acquire a database connection.",
      "probable_cause": "Connection pool size too small, connections not released, or database overloaded.",
      "severity": "HIGH",
      "match_count": 1,
      "matched_lines": [
        "2024-01-15 10:30:30 ERROR DatabaseService - Connection pool exhausted."
      ]
    }
  ],
  "overall_severity": "HIGH",
  "severity_score": 45,
  "severity_confidence": "HIGH",
  "severity_reasoning": [
    "2 ERROR log entries detected",
    "Pattern 'Database Connection Pool Exhausted' detected (1 occurrences)"
  ],
  "affected_services": ["databaseservice"],
  "affected_endpoints": ["/api/orders"],
  "summary": "HIGH incident detected: 2 error(s) found across 1 known incident pattern(s)."
}
```

### `POST /api/incidents/analyze/upload`
Upload a `.log` or `.txt` file (max 50MB) for pattern analysis.
- **Content-Type:** `multipart/form-data`
- **Field:** `file` (binary)

---

## 3. Autonomous Incident Investigation (LangGraph AI Agent)

### `POST /api/investigations/run`
Triggers the full 5-node LangGraph autonomous agent workflow.

**Request Body:**
```json
{
  "logs": "2024-01-15 10:30:30 ERROR DatabaseService - Connection pool exhausted.\n2024-01-15 10:30:31 ERROR HTTP 500 - /api/orders - Internal Server Error",
  "question": "Why is the checkout service failing?"
}
```

**Response `200 OK` (Pydantic `InvestigationReport`):**
```json
{
  "investigation_id": "8f48b991-3e4b-44bb-8b17-1049ad61c775",
  "incident_title": "Database Connection Pool Exhaustion Leading to API Failures",
  "severity": "HIGH",
  "created_at": "2024-01-15T10:31:00Z",
  "executive_summary": "The application suffered an outage due to database pool exhaustion impacting order processing.",
  "technical_summary": "Active connections saturated max pool limits causing 500 status returns on /api/orders.",
  "symptoms": [
    "Database pool capacity at 100%",
    "HTTP 500 status returned on checkout endpoints"
  ],
  "affected_services": ["databaseservice", "orderservice"],
  "affected_endpoints": ["/api/orders"],
  "error_count": 2,
  "warning_count": 0,
  "total_log_entries": 2,
  "detected_patterns": ["DB_CONNECTION_EXHAUSTION", "HTTP_5XX_ERRORS"],
  "probable_root_cause": "[HYPOTHESIS] Connection leak in worker process or under-provisioned pool size under peak concurrency.",
  "alternative_causes": [
    "[HYPOTHESIS] Network partition between application cluster and PostgreSQL primary.",
    "[HYPOTHESIS] Unindexed long-running analytical query blocking connection release."
  ],
  "supporting_evidence": [
    {
      "source": "log",
      "content": "ERROR DatabaseService - Connection pool exhausted.",
      "relevance": "Direct proof of pool capacity failure",
      "line_number": 1
    }
  ],
  "document_references": [
    {
      "document_name": "database_runbook.pdf",
      "source_file": "storage/uploads/database_runbook.pdf",
      "excerpt": "When pool exhaustion occurs, verify connection timeout settings in db_pool.yml",
      "relevance_score": 0.82,
      "page_number": 4
    }
  ],
  "recommended_remediation": [
    {
      "priority": 1,
      "action": "Increase max_connections in database pool from 10 to 50",
      "rationale": "Prevents immediate queue saturation under peak traffic spikes",
      "estimated_impact": "Restores immediate transaction throughput"
    }
  ],
  "immediate_actions": [
    "Restart worker instances to release hung connection handles",
    "Enable connection pool metrics logging"
  ],
  "confidence": "HIGH",
  "confidence_reasoning": "Direct evidence of pool exhaustion present with matching timestamped 500 API responses.",
  "additional_info_required": [
    "Slow query log from PostgreSQL",
    "Connection leak stack traces"
  ],
  "limitations": [
    "Database host CPU and IOPS metrics not supplied in provided log telemetry"
  ]
}
```

### `GET /api/investigations`
List past investigations from SQLite.
- **Query Params:** `limit` (default: 50)
- **Response:** Array of lightweight `InvestigationSummary` objects.

### `GET /api/investigations/{investigation_id}`
Retrieve a single complete `InvestigationReport` by its UUID.

---

## 4. Knowledge Base & Vector Documents (RAG)

### `POST /api/documents/upload`
Uploads runbook/architecture documentation (.pdf, .txt, .md). Chunks text (500 chars, 50 overlap), embeds via Sentence Transformers (`all-MiniLM-L6-v2`), and indexes into ChromaDB.
- **Content-Type:** `multipart/form-data`
- **Field:** `file`

**Response `200 OK`:**
```json
{
  "success": true,
  "document_id": "c71e54fb-d8bf-49c5-8f6a-49a7de03708a",
  "filename": "runbook_database_troubleshooting.pdf",
  "file_type": "pdf",
  "file_size_bytes": 145230,
  "chunk_count": 28,
  "collection_name": "aiops_knowledge_base",
  "message": "Successfully processed 'runbook_database_troubleshooting.pdf' into 28 searchable chunks."
}
```

### `GET /api/documents`
List all ingested knowledge documents.

### `GET /api/documents/stats`
Retrieve ChromaDB collection metrics:
```json
{
  "collection_name": "aiops_knowledge_base",
  "document_count": 28,
  "status": "ready"
}
```
