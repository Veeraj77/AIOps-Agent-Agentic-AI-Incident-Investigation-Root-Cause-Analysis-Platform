"""
AIOps Agent – Application Configuration
========================================
Uses Pydantic Settings to load config from environment variables.
All sensitive values (API keys) come from .env – never hardcoded.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Central application configuration.

    Why Pydantic Settings?
    - Automatically reads from environment variables and .env file.
    - Validates types (e.g., int, bool) automatically.
    - Raises clear errors if required variables are missing.
    - Provides defaults where safe to do so.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = Field(default="AIOps Agent", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # --- Server ---
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # --- LLM Configuration ---
    groq_api_key: str = Field(default="", description="Groq API key")
    llm_provider: str = Field(default="groq", description="LLM provider name")
    llm_model: str = Field(default="qwen/qwen3.8-27b", description="LLM model name")
    llm_temperature: float = Field(default=0.1, description="LLM temperature (0=deterministic)")
    llm_max_tokens: int = Field(default=800, description="Max output tokens for LLM generation")

    # --- Embedding Model (runs locally via Sentence Transformers) ---
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence Transformer model for embeddings",
    )

    # --- Database ---
    database_url: str = Field(
        default="sqlite:///./storage/aiops.db",
        description="SQLite database URL",
    )

    # --- ChromaDB (Vector Store) ---
    chroma_persist_dir: str = Field(
        default="./storage/chroma_db",
        description="ChromaDB persistence directory",
    )
    chroma_collection_name: str = Field(
        default="aiops_knowledge_base",
        description="ChromaDB collection name",
    )

    # --- File Upload ---
    max_file_size_mb: int = Field(default=50, description="Max upload file size in MB")
    allowed_log_extensions: str = Field(default=".log,.txt", description="Allowed log extensions")
    allowed_doc_extensions: str = Field(default=".pdf,.txt,.md", description="Allowed doc extensions")

    # --- CORS ---
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Allowed CORS origins (comma-separated)",
    )

    # --- Storage ---
    storage_dir: str = Field(default="./storage", description="Base storage directory")
    upload_dir: str = Field(default="./storage/uploads", description="Uploads directory")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def allowed_log_ext_list(self) -> List[str]:
        """Parse comma-separated log extensions into a list."""
        return [ext.strip().lower() for ext in self.allowed_log_extensions.split(",")]

    @property
    def allowed_doc_ext_list(self) -> List[str]:
        """Parse comma-separated document extensions into a list."""
        return [ext.strip().lower() for ext in self.allowed_doc_extensions.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB limit to bytes."""
        return self.max_file_size_mb * 1024 * 1024

    def validate_llm_config(self) -> None:
        """
        Raise a clear error if LLM credentials are missing.
        Called at startup so we fail fast rather than during a request.
        """
        if self.llm_provider == "groq" and not self.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Create a free account at https://console.groq.com and add your key to .env"
            )


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    Why lru_cache?
    - Settings are read-only after startup.
    - Avoids re-reading environment variables on every request.
    - Makes the settings a true singleton.
    """
    return Settings()
