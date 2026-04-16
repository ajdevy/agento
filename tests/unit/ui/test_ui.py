"""Tests for UI module."""



class TestUIConsole:
    """Tests for Console class."""

    def test_console_creation(self):
        """Test creating a Console instance."""
        from agento.ui.console import Console

        console = Console()
        assert console is not None

    def test_console_type(self):
        """Test Console is the right type."""
        from agento.ui import Console

        assert Console is not None


class TestUIApp:
    """Tests for App class."""

    def test_app_creation(self):
        """Test creating an App instance."""
        from agento.ui.app import App

        app = App()
        assert app is not None

    def test_app_type(self):
        """Test App is the right type."""
        from agento.ui import App

        assert App is not None


class TestUIModule:
    """Tests for UI module exports."""

    def test_import_console(self):
        """Test Console can be imported from ui."""
        from agento.ui import Console

        assert Console is not None

    def test_import_app(self):
        """Test App can be imported from ui."""
        from agento.ui import App

        assert App is not None

    def test_console_and_app_different(self):
        """Test Console and App are different classes."""
        from agento.ui import App, Console

        assert Console is not App
