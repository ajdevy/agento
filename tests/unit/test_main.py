"""Tests for main module."""

import asyncio
from io import StringIO
from unittest.mock import patch

from agento.main import main, run_tui


class TestMain:
    """Tests for main module."""

    def test_check_api_key(self):
        """Test check_api_key function."""
        from agento.main import check_api_key

        with patch("agento.main.settings") as mock_settings:
            mock_settings.openrouter_api_key.get_secret_value.return_value = "test-key"
            mock_settings.deepseek_api_key = None
            mock_settings.google_api_key = None

            result = check_api_key()
            assert result == "test-key"

    def test_check_api_key_deepseek(self):
        """Test check_api_key with DeepSeek."""
        from agento.main import check_api_key

        with patch("agento.main.settings") as mock_settings:
            mock_settings.openrouter_api_key = None
            mock_settings.deepseek_api_key.get_secret_value.return_value = (
                "deepseek-key"
            )
            mock_settings.google_api_key = None

            result = check_api_key()
            assert result == "deepseek-key"

    def test_check_api_key_no_key(self):
        """Test check_api_key returns None when no key."""
        from agento.main import check_api_key

        with patch("agento.main.settings") as mock_settings:
            mock_settings.openrouter_api_key = None
            mock_settings.deepseek_api_key = None
            mock_settings.google_api_key = None

            result = check_api_key()
            assert result is None

    def test_run_tui_with_missing_api_key(self):
        """Test run_tui exits when no API key and no input."""
        with patch("agento.main.check_api_key", return_value=None):
            with patch("sys.stdin", StringIO("q\n")):
                try:
                    asyncio.run(run_tui())
                except SystemExit as e:
                    assert e.code == 1

    def test_main_function_exists(self):
        """Test main function can be imported."""
        assert main is not None
        assert callable(main)
