"""Tests for main module."""

from unittest.mock import patch


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

    def test_app_creation(self):
        """Test app can be created."""
        from agento.main import app

        assert app is not None
