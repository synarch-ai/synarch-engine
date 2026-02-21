"""Synarch Engine — Configuration via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # --- Database ---
    database_url: str = "postgresql://synarch:synarch_local@localhost:5433/synarch"

    # --- NATS ---
    nats_url: str = "nats://localhost:4222"

    # --- Qdrant ---
    qdrant_url: str = "http://localhost:6333"

    # --- Ollama ---
    ollama_api_base: str = "http://localhost:11434"

    # --- AWS Bedrock ---
    aws_region_name: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    # --- App ---
    app_name: str = "Synarch Engine"
    app_version: str = "0.1.0"
    debug: bool = True
    cors_origins: list[str] = ["http://localhost:3000"]

    # --- Paths ---
    souls_dir: str = "docs/agents"

    # --- Model Routing ---
    model_synarch: str = "bedrock/anthropic.claude-opus-4-20250514-v1:0"
    model_zeus: str = "bedrock/anthropic.claude-sonnet-4-20250514-v1:0"
    model_thoth: str = "bedrock/anthropic.claude-sonnet-4-20250514-v1:0"
    model_hermes: str = "ollama/llama3.1:8b"
    model_hephaestus: str = "bedrock/anthropic.claude-sonnet-4-20250514-v1:0"
    model_janus: str = "bedrock/anthropic.claude-3-5-haiku-20241022-v1:0"
    model_call_budget_cap: int = 24
    budget_counter_ttl_seconds: int = 86400
    require_durable_checkpointer: bool = True

    # --- HITL ---
    approval_timeout_seconds: int = 300
    default_authority_mode: str = "supervised"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- API ---
    idempotency_ttl_seconds: int = 86400
    enable_idempotency_middleware: bool = True

    # Prefer local developer overrides in .env.local, then fall back to .env.
    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Singleton settings instance."""
    return Settings()
