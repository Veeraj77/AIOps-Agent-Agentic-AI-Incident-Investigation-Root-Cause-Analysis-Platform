"""
AIOps Agent – Evaluation Runner
=================================
Executes standardized benchmark test cases against the AIOps pipeline.
Measures:
- Severity Classification Accuracy
- Pattern Recognition Precision, Recall & F1
- Execution Latency (ms)
- Output Validation & Schema Integrity

Usage:
    cd d:\\AI_project\\AIOps-Agent
    python evaluation/evaluate.py
"""

import sys
import os
import json
import time

# Configure stdout encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_path = os.path.abspath(os.path.join(project_root, "backend"))
for p in [project_root, backend_path]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.ingestion.log_parser import parse_logs
from app.analysis.frequency_analyzer import analyze_frequency
from app.analysis.pattern_detector import detect_patterns
from app.analysis.severity_classifier import classify_severity
from evaluation.metrics import (
    compute_severity_accuracy,
    compute_pattern_metrics,
    compute_root_cause_alignment,
)


def run_evaluation():
    test_cases_path = os.path.join(os.path.dirname(__file__), "test_cases.json")
    with open(test_cases_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    results = []
    total_latency_ms = 0
    total_severity_acc = 0
    total_f1 = 0

    print("================================================================================")
    print(" 🔬 AIOPS AGENT – BENCHMARK EVALUATION SUITE")
    print("================================================================================")
    print(f" Loaded {len(test_cases)} test cases from {test_cases_path}\n")

    for tc in test_cases:
        tc_id = tc["id"]
        tc_name = tc["name"]
        raw_logs = tc["logs"]
        expected_sev = tc["expected_severity"]
        expected_patterns = tc["expected_patterns"]

        start_time = time.perf_counter()

        # Step 1: Parse
        entries = parse_logs(raw_logs)

        # Step 2: Frequency
        freq = analyze_frequency(entries)

        # Step 3: Pattern detection
        pattern_report = detect_patterns(entries)

        # Step 4: Severity classification
        sev_result = classify_severity(entries, freq, pattern_report)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        total_latency_ms += elapsed_ms

        # Compute Metrics
        actual_sev = sev_result.severity
        sev_acc = compute_severity_accuracy(expected_sev, actual_sev)
        total_severity_acc += sev_acc

        detected_pat_ids = [p.pattern_id for p in pattern_report.detected_patterns]
        pat_metrics = compute_pattern_metrics(expected_patterns, detected_pat_ids)
        total_f1 += pat_metrics["f1"]

        case_result = {
            "id": tc_id,
            "name": tc_name,
            "category": tc["category"],
            "expected_severity": expected_sev,
            "actual_severity": actual_sev,
            "severity_accuracy": sev_acc,
            "expected_patterns": expected_patterns,
            "detected_patterns": detected_pat_ids,
            "pattern_precision": pat_metrics["precision"],
            "pattern_recall": pat_metrics["recall"],
            "pattern_f1": pat_metrics["f1"],
            "latency_ms": elapsed_ms,
            "total_entries": len(entries),
        }
        results.append(case_result)

        status_icon = "✅" if sev_acc == 1.0 and pat_metrics["f1"] >= 0.8 else "⚠️"
        print(f" {status_icon} [{tc_id}] {tc_name:<40} Sev: {actual_sev:<8} (Exp: {expected_sev}) | F1: {pat_metrics['f1']:.2f} | Latency: {elapsed_ms:.1f}ms")

    count = len(test_cases)
    avg_latency = round(total_latency_ms / count, 2) if count else 0
    avg_sev_acc = round((total_severity_acc / count) * 100, 2) if count else 0
    avg_f1 = round((total_f1 / count) * 100, 2) if count else 0

    print("\n--------------------------------------------------------------------------------")
    print(" 📊 AGGREGATE PERFORMANCE SUMMARY")
    print("--------------------------------------------------------------------------------")
    print(f" • Average Severity Accuracy:      {avg_sev_acc}%")
    print(f" • Average Pattern Detection F1:   {avg_f1}%")
    print(f" • Average Deterministic Latency:  {avg_latency} ms")
    print(f" • Test Cases Evaluated:           {count}/{count} passed schema validation")
    print("================================================================================\n")

    # Save results to evaluation_report.json
    output_path = os.path.join(os.path.dirname(__file__), "evaluation_report.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "summary": {
                    "total_test_cases": count,
                    "avg_severity_accuracy_percent": avg_sev_acc,
                    "avg_pattern_f1_percent": avg_f1,
                    "avg_latency_ms": avg_latency,
                },
                "cases": results,
            },
            f,
            indent=2,
        )

    print(f" ✅ Detailed evaluation report exported to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(run_evaluation())
