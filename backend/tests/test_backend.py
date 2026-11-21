"""
AIOps Agent – Backend Tests
=============================
Tests for core log parsing, analysis, and API endpoints.

Run with: pytest tests/ -v (from the backend/ directory)
"""

import pytest
from fastapi.testclient import TestClient


# ── Sample Log Data ───────────────────────────────────────────────────────────

SAMPLE_LOGS_DB_INCIDENT = """
2024-01-15 10:30:30 ERROR DatabaseService - Connection pool exhausted. No available connections.
2024-01-15 10:30:31 ERROR OrderService - Failed to process order: Database connection timeout after 30000ms
2024-01-15 10:30:32 WARNING APIGateway - API response time exceeded 5000ms for /api/orders
2024-01-15 10:30:33 ERROR HTTP 500 - /api/orders - Internal Server Error
2024-01-15 10:30:34 INFO CacheService - Cache hit rate: 92%
"""

SAMPLE_LOGS_AUTH_INCIDENT = """
ERROR: JWT token validation failed - invalid signature
ERROR: Authentication failed for user admin@example.com
ERROR: HTTP 401 - /api/auth/login - Unauthorized
CRITICAL: All authentication requests failing
"""

SAMPLE_LOGS_CLEAN = """
INFO: Application started
INFO: Health check passed
INFO: Processing request /api/users
INFO: Request completed in 45ms
"""


# ── Tests: Log Parser ─────────────────────────────────────────────────────────

class TestLogParser:
    """Tests for app.ingestion.log_parser"""

    def test_parse_basic_error_logs(self):
        from app.ingestion.log_parser import parse_logs
        entries = parse_logs("ERROR: Database connection timeout\nWARNING: High memory usage")
        assert len(entries) == 2
        assert entries[0].level == "ERROR"
        assert entries[1].level == "WARNING"

    def test_parse_timestamped_logs(self):
        from app.ingestion.log_parser import parse_logs
        entries = parse_logs("2024-01-15 10:30:30 ERROR ServiceA - Connection failed")
        assert len(entries) == 1
        assert entries[0].level == "ERROR"
        assert entries[0].service == "ServiceA"
        assert entries[0].timestamp is not None

    def test_parse_empty_raises(self):
        from app.ingestion.log_parser import parse_logs
        from app.core.exceptions import LogParsingError
        with pytest.raises(LogParsingError):
            parse_logs("")

    def test_parse_whitespace_only_raises(self):
        from app.ingestion.log_parser import parse_logs
        from app.core.exceptions import LogParsingError
        with pytest.raises(LogParsingError):
            parse_logs("   \n   \n   ")

    def test_parse_multiple_formats(self):
        from app.ingestion.log_parser import parse_logs
        mixed_logs = """
ERROR: Simple error format
2024-01-15 10:00:00 WARNING ServiceB - Timestamped warning
[ERROR] Bracket format error
"""
        entries = parse_logs(mixed_logs)
        levels = [e.level for e in entries]
        assert "ERROR" in levels
        assert "WARNING" in levels

    def test_endpoint_extraction(self):
        from app.ingestion.log_parser import parse_log_line
        entry = parse_log_line("ERROR: HTTP 500 - /api/orders - Internal Server Error")
        assert entry is not None
        assert any("/api/orders" in ep for ep in entry.endpoints) or "/api/orders" in entry.message

    def test_severity_weight_ordering(self):
        from app.ingestion.log_parser import parse_logs
        entries = parse_logs("CRITICAL: Crash\nERROR: Failure\nWARNING: Issue\nINFO: OK")
        weights = [e.severity_weight for e in entries]
        assert weights[0] > weights[1] > weights[2] > weights[3]


# ── Tests: Frequency Analyzer ─────────────────────────────────────────────────

class TestFrequencyAnalyzer:
    """Tests for app.analysis.frequency_analyzer"""

    def test_frequency_counts_errors(self):
        from app.ingestion.log_parser import parse_logs
        from app.analysis.frequency_analyzer import analyze_frequency
        entries = parse_logs(SAMPLE_LOGS_DB_INCIDENT)
        freq = analyze_frequency(entries)
        assert freq.level_counts.get("ERROR", 0) >= 2
        assert freq.level_counts.get("WARNING", 0) >= 1

    def test_error_rate_calculation(self):
        from app.ingestion.log_parser import parse_logs
        from app.analysis.frequency_analyzer import analyze_frequency
        # 3 errors out of 4 total = 75%
        entries = parse_logs("ERROR: A\nERROR: B\nERROR: C\nINFO: D")
        freq = analyze_frequency(entries)
        assert freq.error_rate == 75.0

    def test_top_errors_sorted(self):
        from app.ingestion.log_parser import parse_logs
        from app.analysis.frequency_analyzer import analyze_frequency
        # Same error 3 times
        entries = parse_logs("ERROR: DB timeout\nERROR: DB timeout\nERROR: DB timeout\nERROR: Network error")
        freq = analyze_frequency(entries)
        assert len(freq.top_errors) > 0
        assert freq.top_errors[0]["message"] == "DB timeout"
        assert freq.top_errors[0]["count"] == 3

    def test_empty_entries_returns_empty_report(self):
        from app.analysis.frequency_analyzer import analyze_frequency
        freq = analyze_frequency([])
        assert freq.total_entries == 0
        assert freq.error_rate == 0.0


# ── Tests: Pattern Detector ───────────────────────────────────────────────────

class TestPatternDetector:
    """Tests for app.analysis.pattern_detector"""

    def test_detect_db_exhaustion(self):
        from app.ingestion.log_parser import parse_logs
        from app.analysis.pattern_detector import detect_patterns
        entries = parse_logs("ERROR: Connection pool exhausted\nERROR: Database connection timeout")
        report = detect_patterns(entries)
        pattern_ids = [p.pattern_id for p in report.detected_patterns]
        assert "DB_CONNECTION_EXHAUSTION" in pattern_ids

    def test_detect_http_5xx(self):
        from app.ingestion.log_parser import parse_logs
        from app.analysis.pattern_detector import detect_patterns
        entries = parse_logs("ERROR: HTTP 500 - /api/orders - Internal Server Error")
        report = detect_patterns(entries)
        pattern_ids = [p.pattern_id for p in report.detected_patterns]
        assert "HTTP_5XX_ERRORS" in pattern_ids

    def test_clean_logs_no_patterns(self):
        from app.ingestion.log_parser import parse_logs
        from app.analysis.pattern_detector import detect_patterns
        entries = parse_logs(SAMPLE_LOGS_CLEAN)
        report = detect_patterns(entries)
        assert report.total_patterns_found == 0

    def test_patterns_sorted_by_severity(self):
        from app.ingestion.log_parser import parse_logs
        from app.analysis.pattern_detector import detect_patterns
        entries = parse_logs(SAMPLE_LOGS_DB_INCIDENT)
        report = detect_patterns(entries)
        if len(report.detected_patterns) >= 2:
            severities = [p.severity for p in report.detected_patterns]
            # CRITICAL should come before HIGH, HIGH before MEDIUM
            severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
            for i in range(len(severities) - 1):
                assert severity_order.get(severities[i], 0) >= severity_order.get(severities[i + 1], 0)


# ── Tests: Severity Classifier ────────────────────────────────────────────────

class TestSeverityClassifier:
    """Tests for app.analysis.severity_classifier"""

    def test_critical_logs_get_high_severity(self):
        from app.ingestion.log_parser import parse_logs
        from app.analysis.frequency_analyzer import analyze_frequency
        from app.analysis.pattern_detector import detect_patterns
        from app.analysis.severity_classifier import classify_severity
        entries = parse_logs("CRITICAL: System crash\nCRITICAL: OOM error\nCRITICAL: Data loss")
        freq = analyze_frequency(entries)
        patterns = detect_patterns(entries)
        result = classify_severity(entries, freq, patterns)
        assert result.severity in ("CRITICAL", "HIGH")

    def test_info_only_logs_get_low_severity(self):
        from app.ingestion.log_parser import parse_logs
        from app.analysis.frequency_analyzer import analyze_frequency
        from app.analysis.pattern_detector import detect_patterns
        from app.analysis.severity_classifier import classify_severity
        entries = parse_logs(SAMPLE_LOGS_CLEAN)
        freq = analyze_frequency(entries)
        patterns = detect_patterns(entries)
        result = classify_severity(entries, freq, patterns)
        assert result.severity in ("LOW", "INFO")

    def test_severity_result_has_reasoning(self):
        from app.ingestion.log_parser import parse_logs
        from app.analysis.frequency_analyzer import analyze_frequency
        from app.analysis.pattern_detector import detect_patterns
        from app.analysis.severity_classifier import classify_severity
        entries = parse_logs(SAMPLE_LOGS_DB_INCIDENT)
        freq = analyze_frequency(entries)
        patterns = detect_patterns(entries)
        result = classify_severity(entries, freq, patterns)
        assert len(result.reasoning) > 0
        assert result.score > 0


# ── Tests: API Endpoints ──────────────────────────────────────────────────────

class TestAPIEndpoints:
    """Integration tests for FastAPI endpoints."""

    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Create a test client for each test."""
        import os
        os.environ.setdefault("GROQ_API_KEY", "test-key-placeholder")
        from app.main import app
        from app.database.connection import init_db
        init_db()
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self):
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "AIOps Agent" in data["message"]

    def test_analyze_incident_success(self):
        response = self.client.post(
            "/api/incidents/analyze",
            json={"logs": SAMPLE_LOGS_DB_INCIDENT},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_log_entries"] > 0
        assert "overall_severity" in data
        assert len(data["detected_patterns"]) > 0

    def test_analyze_incident_empty_logs_returns_422(self):
        response = self.client.post(
            "/api/incidents/analyze",
            json={"logs": ""},
        )
        assert response.status_code == 422

    def test_analyze_incident_whitespace_returns_error(self):
        response = self.client.post(
            "/api/incidents/analyze",
            json={"logs": "   "},
        )
        assert response.status_code in (422, 400)

    def test_list_investigations_returns_list(self):
        response = self.client.get("/api/investigations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_nonexistent_investigation_returns_404(self):
        response = self.client.get("/api/investigations/nonexistent-uuid")
        assert response.status_code == 404

    def test_list_documents_returns_list(self):
        response = self.client.get("/api/documents")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_document_stats_endpoint(self):
        response = self.client.get("/api/documents/stats")
        assert response.status_code == 200
        data = response.json()
        assert "document_count" in data
        assert "status" in data
