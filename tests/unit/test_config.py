"""Tests for configuration."""

import os
from unittest.mock import patch

from agento.config import Settings


class TestSettings:
    """Tests for Settings."""

    def test_settings_defaults(self):
        """Test default settings."""
        settings = Settings()

        assert settings.default_model == "openrouter/free"
        assert settings.autonomy_level == 1
        assert settings.docker_enabled is True
        assert settings.mcp_enabled is True

    def test_has_api_key_none(self):
        """Test has_api_key with no keys."""
        with patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "", "DEEPSEEK_API_KEY": "", "GOOGLE_API_KEY": ""},
            clear=True,
        ):
            with patch.object(
                Settings,
                "model_config",
                {"env_file": ".env.non_existent", "extra": "ignore"},
            ):
                settings = Settings(_env_file=".env.non_existent")
                assert settings.has_api_key is False

    def test_has_api_key_with_key(self):
        """Test has_api_key with key set."""
        settings = Settings(openrouter_api_key="sk-test-key")

        assert settings.has_api_key is True

    def test_memory_dir_default(self):
        """Test memory directory default."""
        settings = Settings()

        assert settings.memory_dir == "./memory_data"

    def test_max_command_timeout(self):
        """Test max command timeout."""
        settings = Settings()

        assert settings.max_command_timeout == 300
