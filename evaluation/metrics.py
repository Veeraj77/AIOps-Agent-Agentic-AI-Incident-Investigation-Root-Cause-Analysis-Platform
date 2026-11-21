"""
AIOps Agent – Evaluation Metrics
==================================
Calculates objective quantitative metrics for evaluating:
1. Severity classification accuracy
2. Pattern detection precision & recall
3. Unsupported claim rate (hallucination detection)
4. Root cause keyword alignment
5. End-to-end response latency
"""

from typing import List, Dict, Any, Set


def compute_severity_accuracy(expected: str, actual: str) -> float:
    """
    Computes severity match score.
    Exact match = 1.0, Adjacent level match = 0.5, Mismatch = 0.0.
    """
    levels = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    exp = (expected or "").upper()
    act = (actual or "").upper()

    if exp == act:
        return 1.0

    try:
        exp_idx = levels.index(exp)
        act_idx = levels.index(act)
        if abs(exp_idx - act_idx) == 1:
            return 0.5
    except ValueError:
        pass

    return 0.0


def compute_pattern_metrics(expected_patterns: List[str], detected_patterns: List[str]) -> Dict[str, float]:
    """
    Computes precision, recall, and F1 score for detected error patterns.
    """
    exp_set: Set[str] = set(expected_patterns)
    det_set: Set[str] = set(detected_patterns)

    if not exp_set and not det_set:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    if not exp_set or not det_set:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    true_positives = len(exp_set.intersection(det_set))
    precision = true_positives / len(det_set) if det_set else 0.0
    recall = true_positives / len(exp_set) if exp_set else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def compute_unsupported_claim_rate(raw_logs: str, evidence_items: List[Dict[str, Any]]) -> float:
    """
    Calculates the unsupported claim rate (hallucination rate).
    Fraction of cited log evidence that does NOT appear in original raw logs.
    Target: 0.0 (no fabricated evidence).
    """
    if not evidence_items:
        return 0.0

    unsupported_count = 0
    norm_logs = raw_logs.lower()

    for item in evidence_items:
        content = item.get("content", "").strip().lower()
        if not content:
            continue
        # Check if content or a substantial portion of it is present in raw logs
        if content not in norm_logs and not any(line in norm_logs for line in content.splitlines() if len(line.strip()) > 15):
            unsupported_count += 1

    return round(unsupported_count / len(evidence_items), 4)


def compute_root_cause_alignment(expected_keywords: List[str], root_cause_text: str) -> float:
    """
    Checks what proportion of expected diagnostic keywords appear in root cause text.
    """
    if not expected_keywords:
        return 1.0

    text_lower = (root_cause_text or "").lower()
    matches = sum(1 for kw in expected_keywords if kw.lower() in text_lower)
    return round(matches / len(expected_keywords), 4)
