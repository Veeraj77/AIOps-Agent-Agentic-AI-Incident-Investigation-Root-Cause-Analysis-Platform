"""
AIOps Agent – LLM Prompts
===========================
Centralised prompt templates for all agent nodes.

Why separate prompts from code?
- Easy to tweak and improve prompts without touching logic.
- Prompts are essentially the "configuration" of the AI behaviour.
- Keeps node code focused on data flow, not string formatting.

Design principles:
- Always instruct the LLM to separate FACTS from HYPOTHESES.
- Always instruct the LLM to cite evidence.
- Never allow the LLM to claim certainty about root causes.
"""


SYSTEM_UNDERSTAND_INCIDENT = """You are an expert Site Reliability Engineer (SRE) and DevOps specialist.
Your job is to analyse application incident logs and identify the nature of the incident.
Be precise, technical, and evidence-based.
Never fabricate information not present in the logs.
Always distinguish between OBSERVED FACTS (from logs) and HYPOTHESES (your analysis)."""


PROMPT_UNDERSTAND_INCIDENT = """
You are starting an incident investigation. Analyse the logs below and produce a structured understanding.

USER QUESTION: {question}

RAW LOGS:
{logs}

PRELIMINARY ANALYSIS:
- Total log entries: {total_entries}
- Error count: {error_count}
- Warning count: {warning_count}
- Overall severity: {severity}
- Detected patterns: {patterns}
- Affected services: {services}

Your task:
1. Write a short incident title (max 10 words).
2. Write an executive summary (2-3 sentences, non-technical).
3. Write a technical summary (3-5 sentences, for engineers).
4. List the observable symptoms (what is happening, as bullet points).

IMPORTANT:
- Only state what is DIRECTLY OBSERVABLE in the logs.
- Do not guess root causes yet.
- Do not add information not in the logs.

Respond in this exact JSON format:
{{
  "incident_title": "...",
  "executive_summary": "...",
  "technical_summary": "...",
  "symptoms": ["symptom1", "symptom2", "..."]
}}
"""


SYSTEM_INVESTIGATE_ROOT_CAUSE = """You are a senior Site Reliability Engineer performing root cause analysis.
You have log data, pattern analysis, and optionally relevant documentation.
Your analysis must be:
- Evidence-based (cite specific log lines)
- Clearly labelled as HYPOTHESIS where appropriate
- Actionable (provide specific remediation steps)
- Honest about uncertainty"""


PROMPT_INVESTIGATE_ROOT_CAUSE = """
Perform root cause analysis for this incident.

INCIDENT TITLE: {incident_title}
SEVERITY: {severity}
USER QUESTION: {question}

OBSERVED SYMPTOMS:
{symptoms}

DETECTED ERROR PATTERNS:
{patterns}

TOP ERRORS (by frequency):
{top_errors}

RELEVANT DOCUMENTATION FROM KNOWLEDGE BASE:
{context}

TASK:
1. Identify the most probable root cause. Mark this clearly as [HYPOTHESIS].
2. List 1-2 alternative causes to investigate. Mark as [HYPOTHESIS].
3. List supporting evidence from the logs (quote actual log lines).
4. Provide 3-5 specific remediation steps (prioritised).
5. List immediate actions to restore service.
6. Assess your confidence: HIGH, MEDIUM, or LOW.
7. State what additional information would improve your diagnosis.

RULES:
- Do NOT present unverified hypotheses as confirmed facts.
- Every claim must reference a specific log line or pattern.
- If you are uncertain, say so.

Respond in this exact JSON format:
{{
  "probable_root_cause": "[HYPOTHESIS] ...",
  "alternative_causes": ["[HYPOTHESIS] ...", "..."],
  "supporting_evidence": [
    {{"source": "log", "content": "actual log line here", "relevance": "why relevant"}}
  ],
  "remediation_steps": [
    {{"priority": 1, "action": "...", "rationale": "...", "estimated_impact": "..."}}
  ],
  "immediate_actions": ["action1", "action2"],
  "confidence": "MEDIUM",
  "confidence_reasoning": "...",
  "additional_info_required": ["info1", "info2"],
  "limitations": ["limitation1"]
}}
"""


PROMPT_VALIDATE_EVIDENCE = """
Review the following root cause analysis and validate that:
1. Each claim is supported by actual log evidence.
2. No information has been fabricated.
3. The confidence level is appropriate.

ROOT CAUSE ANALYSIS:
{root_cause_analysis}

ACTUAL LOG EVIDENCE:
{log_evidence}

If the analysis is well-supported, respond: {{"valid": true, "issues": []}}
If there are unsupported claims, respond: {{"valid": false, "issues": ["issue1", "issue2"]}}
"""
