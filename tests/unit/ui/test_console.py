"""Tests for console module."""

from unittest.mock import patch


class TestConsole:
    """Tests for Console class."""

    def test_console_creation(self):
        """Test console creation."""
        from agento.ui.console import Console

        console = Console()
        assert console is not None

    def test_print(self):
        """Test print method."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "print") as mock_print:
            console.print("Hello")
            mock_print.assert_called_once_with("Hello")

    def test_print_markdown(self):
        """Test markdown printing."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "print") as mock_print:
            console.print_markdown("**Bold**")
            mock_print.assert_called_once()

    def test_print_code(self):
        """Test code printing."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "print") as mock_print:
            console.print_code("print('hello')", language="python")
            mock_print.assert_called_once()

    def test_print_panel(self):
        """Test panel printing."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "print") as mock_print:
            console.print_panel("Content", title="Title")
            mock_print.assert_called_once()

    def test_print_table(self):
        """Test table printing."""
        from agento.ui.console import Console

        console = Console()

        data = [{"name": "Alice", "age": "30"}]

        with patch.object(console._console, "print") as mock_print:
            console.print_table(data, title="People")
            mock_print.assert_called_once()

    def test_print_table_empty(self):
        """Test table printing with empty data."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "print") as mock_print:
            console.print_table([])
            mock_print.assert_not_called()

    def test_print_info(self):
        """Test info printing."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "print") as mock_print:
            console.print_info("Info message")
            mock_print.assert_called_once()

    def test_print_success(self):
        """Test success printing."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "print") as mock_print:
            console.print_success("Success!")
            mock_print.assert_called_once()

    def test_print_warning(self):
        """Test warning printing."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "print") as mock_print:
            console.print_warning("Warning!")
            mock_print.assert_called_once()

    def test_print_error(self):
        """Test error printing."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "print") as mock_print:
            console.print_error("Error!")
            mock_print.assert_called_once()

    def test_print_model_info(self):
        """Test model info printing."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "print") as mock_print:
            console.print_model_info("openrouter/free", 0.0, 100)
            mock_print.assert_called_once()

    def test_print_cost_preview(self):
        """Test cost preview printing."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "print") as mock_print:
            console.print_cost_preview("openrouter/free", 0.0)
            mock_print.assert_called_once()

    def test_input(self):
        """Test input method."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "input", return_value="user input"):
            result = console.input("> ")
            assert result == "user input"

    def test_clear(self):
        """Test clear method."""
        from agento.ui.console import Console

        console = Console()

        with patch.object(console._console, "clear") as mock_clear:
            console.clear()
            mock_clear.assert_called_once()


class TestConsoleModule:
    """Tests for console module-level instance."""

    def test_console_instance(self):
        """Test module-level console instance."""
        from agento.ui.console import console

        assert console is not None
        assert hasattr(console, "print")
