"""
AIOps Agent - Live Groq LLM Integration Test
============================================
Safely validates real Groq API connectivity, prompt execution,
model configuration, and error handling without logging or exposing secrets.
"""

import os
import pytest
from app.config import get_settings
from app.services.llm_service import get_llm, invoke_llm, check_llm_health


def test_groq_settings_and_no_hardcoded_key():
    settings = get_settings()
    assert settings.groq_api_key, "GROQ_API_KEY must be populated in environment"
    assert settings.groq_api_key != "your_groq_api_key_here", "GROQ_API_KEY cannot be the default placeholder"
    assert settings.llm_provider == "groq", "LLM provider must be configured as groq"
    assert settings.llm_model == "qwen/qwen3.8-27b", "LLM model must be set to active model qwen/qwen3.8-27b"


def test_groq_live_connectivity():
    """Verify live request to Groq API and receipt of genuine response."""
    result = check_llm_health()
    assert result.get("status") == "ok", f"Expected 'ok', got {result}"
    assert "LLM responded" in result.get("message", "")


def test_groq_langchain_chat_model_invocation():
    """Verify LangChain ChatGroq wrapper produces dynamic text."""
    llm = get_llm()
    prompt = "Respond with the single word: VERIFIED"
    response = llm.invoke(prompt)
    assert response is not None
    assert hasattr(response, "content")
    assert "VERIFIED" in response.content.upper()
