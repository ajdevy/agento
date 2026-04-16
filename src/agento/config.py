"""Agento configuration."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Agento settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM API Keys
    openrouter_api_key: SecretStr | None = Field(
        default=None,
        description="OpenRouter API key",
    )
    deepseek_api_key: SecretStr | None = Field(
        default=None,
        description="DeepSeek API key",
    )
    google_api_key: SecretStr | None = Field(
        default=None,
        description="Google AI API key",
    )

    # Model Configuration
    default_model: str = Field(
        default="openrouter/free",
        description="Default model for all tasks",
    )
    code_model: str | None = Field(
        default=None,
        description="Model for code generation",
    )
    devops_model: str | None = Field(
        default=None,
        description="Model for DevOps tasks",
    )
    planning_model: str | None = Field(
        default=None,
        description="Model for planning",
    )

    # Memory
    memory_dir: str = Field(
        default="./memory_data",
        description="Directory for memory persistence",
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model for vector store",
    )

    # Docker
    docker_enabled: bool = Field(
        default=True,
        description="Enable Docker for command isolation",
    )
    docker_socket: str = Field(
        default="/var/run/docker.sock",
        description="Docker socket path",
    )

    # MCP
    mcp_enabled: bool = Field(
        default=True,
        description="Enable MCP support",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Log level",
    )
    log_file: str | None = Field(
        default=None,
        description="Log file path",
    )

    # Safety
    autonomy_level: Literal[0, 1, 2] = Field(
        default=1,
        description="Autonomy level: 0=confirm all, 1=safe auto, 2=full auto",
    )
    allow_dangerous_commands: bool = Field(
        default=False,
        description="Allow dangerous commands (rm -rf, etc.)",
    )
    max_command_timeout: int = Field(
        default=300,
        description="Maximum command timeout in seconds",
    )

    @property
    def has_api_key(self) -> bool:
        """Check if any API key is configured."""
        return any([
            self.openrouter_api_key and self.openrouter_api_key.get_secret_value(),
            self.deepseek_api_key and self.deepseek_api_key.get_secret_value(),
            self.google_api_key and self.google_api_key.get_secret_value(),
        ])


settings = Settings()
