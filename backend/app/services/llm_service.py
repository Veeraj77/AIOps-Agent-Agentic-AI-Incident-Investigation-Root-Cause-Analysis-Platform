"""
AIOps Agent – LLM Service
===========================
Provides a reusable, provider-agnostic interface to Large Language Models.

Currently supported providers:
- Groq (default) – Fast inference, free tier available at console.groq.com

Why abstract the LLM behind a service?
- If Groq is unavailable, we switch providers by changing one env variable.
- Routes and agents don't depend on the specific LLM library.
- Makes unit testing easier (mock the service, not the LLM).

Groq free-tier models (as of 2024):
- llama3-8b-8192       (fast, good for most tasks)
- llama3-70b-8192      (slower, more accurate)
- mixtral-8x7b-32768   (great for complex reasoning)
- gemma-7b-it          (Google's Gemma model)
"""

from typing import Optional, List
from functools import lru_cache
from app.config import get_settings
from app.core.logging import get_logger
from app.core.exceptions import LLMServiceError, LLMConfigurationError

logger = get_logger(__name__)
settings = get_settings()


@lru_cache(maxsize=1)
def get_llm():
    """
    Create and cache the LangChain LLM client.

    Why lru_cache?
    - Creating an LLM client validates the API key and sets up connections.
    - We only want to do this once at startup.

    Returns:
        A LangChain chat model compatible with .invoke() and .stream().

    Raises:
        LLMConfigurationError: If API credentials are missing.
        LLMServiceError: If the provider is unavailable.
    """
    provider = settings.llm_provider.lower()

    if provider == "groq":
        return _create_groq_llm()
    else:
        raise LLMConfigurationError(
            f"Unknown LLM provider: '{provider}'. Supported: 'groq'"
        )


def _create_groq_llm():
    """
    Create a Groq LangChain chat model.

    Required env variable: GROQ_API_KEY
    Get a free key at: https://console.groq.com
    """
    if not settings.groq_api_key:
        raise LLMConfigurationError(
            "GROQ_API_KEY is not set in .env. "
            "Get your free key at https://console.groq.com"
        )

    try:
        from langchain_groq import ChatGroq

        llm = ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            max_retries=3,
        )
        logger.info(
            "Groq LLM initialised",
            model=settings.llm_model,
            temperature=settings.llm_temperature,
        )
        return llm

    except ImportError:
        raise LLMConfigurationError(
            "langchain-groq is not installed. Run: pip install langchain-groq"
        )
    except Exception as e:
        raise LLMServiceError(f"Failed to initialise Groq LLM: {str(e)}")


def invoke_llm(prompt: str, system_message: Optional[str] = None) -> str:
    """
    Send a prompt to the LLM and return the response text.

    Args:
        prompt:         The user message / task description.
        system_message: Optional system instruction for the LLM.

    Returns:
        The LLM's text response.

    Raises:
        LLMServiceError: If the API call fails.
        LLMConfigurationError: If credentials are missing.
    """
    from langchain_core.messages import HumanMessage, SystemMessage

    llm = get_llm()
    messages = []

    if system_message:
        messages.append(SystemMessage(content=system_message))
    messages.append(HumanMessage(content=prompt))

    try:
        response = llm.invoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        logger.info("LLM invocation successful", prompt_len=len(prompt), response_len=len(content))
        return content
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "auth" in error_msg.lower():
            raise LLMConfigurationError(
                "Invalid Groq API key. Check your GROQ_API_KEY in .env"
            )
        if "429" in error_msg or "rate" in error_msg.lower():
            raise LLMServiceError(
                "Groq API rate limit exceeded. Wait a moment and try again."
            )
        raise LLMServiceError(f"LLM call failed: {error_msg}")


def check_llm_health() -> dict:
    """
    Test LLM connectivity with a minimal prompt.

    Returns:
        dict with 'status' ('ok' or 'error') and 'message'.
    """
    try:
        response = invoke_llm("Reply with just the word: OK")
        return {"status": "ok", "message": f"LLM responded: {response[:50]}"}
    except LLMConfigurationError as e:
        return {"status": "config_error", "message": str(e)}
    except LLMServiceError as e:
        return {"status": "service_error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
