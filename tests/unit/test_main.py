"""Tests for main module."""

from unittest.mock import MagicMock, patch

import pytest


class TestMain:
    """Tests for main module."""

    def test_run_without_api_key(self, capsys):
        """Test run exits when no API key is configured."""
        mock_settings = MagicMock()
        mock_settings.has_api_key = False
        mock_settings.default_model = "openrouter/free"

        with patch("agento.main.settings", mock_settings):
            from agento.main import run

            with pytest.raises(SystemExit) as exc_info:
                run()

            assert exc_info.value.code == 1

            captured = capsys.readouterr()
            assert "No API key configured" in captured.out

    def test_run_with_api_key(self, capsys):
        """Test run succeeds when API key is configured."""
        mock_settings = MagicMock()
        mock_settings.has_api_key = True
        mock_settings.default_model = "openrouter/free"

        with patch("agento.main.settings", mock_settings):
            from agento.main import run

            run()

            captured = capsys.readouterr()
            assert "Configuration loaded successfully" in captured.out
            assert "openrouter/free" in captured.out

    def test_run_with_custom_model(self, capsys):
        """Test run with custom model configuration."""
        mock_settings = MagicMock()
        mock_settings.has_api_key = True
        mock_settings.default_model = "qwen/qwen3-coder-480b-a35b:free"

        with patch("agento.main.settings", mock_settings):
            from agento.main import run

            run()

            captured = capsys.readouterr()
            assert "Configuration loaded successfully" in captured.out
            assert "qwen/qwen3-coder-480b-a35b:free" in captured.out

    def test_run_import_error(self, capsys):
        """Test run handles ImportError gracefully."""
        mock_settings = MagicMock()
        mock_settings.has_api_key = True
        mock_settings.default_model = "openrouter/free"

        with patch("agento.main.settings", mock_settings):
            from agento.main import run

            run()

            captured = capsys.readouterr()
            assert "Agent initialization complete" in captured.out
