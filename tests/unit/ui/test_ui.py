"""Tests for UI module."""



class TestUIConsole:
    """Tests for Console class."""

    def test_console_creation(self):
        """Test creating a Console instance."""
        from agento.ui.console import Console

        console = Console()
        assert console is not None
        assert hasattr(console, "_console")

    def test_console_type(self):
        """Test Console is the right type."""
        from agento.ui.console import Console

        assert Console is not None


class TestUIApp:
    """Tests for TUIApp class."""

    def test_app_creation(self):
        """Test creating a TUIApp instance."""
        from agento.ui.app import TUIApp

        app = TUIApp()
        assert app is not None
        assert hasattr(app, "console")
        assert hasattr(app, "messages")
        assert app._running is False

    def test_app_with_handler(self):
        """Test creating app with message handler."""
        from agento.ui.app import TUIApp

        async def handler(msg):
            return f"Echo: {msg}"

        app = TUIApp(on_message=handler)
        assert app.on_message is handler

    def test_render_header(self):
        """Test rendering header."""
        from agento.ui.app import TUIApp

        app = TUIApp()
        panel = app.render_header()
        assert panel is not None

    def test_render_messages_empty(self):
        """Test rendering empty messages."""
        from agento.ui.app import TUIApp

        app = TUIApp()
        panel = app.render_messages()
        assert panel is not None

    def test_render_messages_with_content(self):
        """Test rendering messages with content."""
        from agento.core.state import Message
        from agento.ui.app import TUIApp

        app = TUIApp()
        app.messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!"),
        ]
        panel = app.render_messages()
        assert panel is not None

    def test_render_status(self):
        """Test rendering status."""
        from agento.ui.app import TUIApp

        app = TUIApp()
        panel = app.render_status()
        assert panel is not None

    def test_render_status_with_state(self):
        """Test rendering status with agent state."""
        from agento.core.state import AgentState
        from agento.ui.app import TUIApp

        app = TUIApp()
        state = AgentState(model="openrouter/free", cost_total=0.05)
        app.update_state(state)

        panel = app.render_status()
        assert panel is not None

    def test_render_model_selector(self):
        """Test rendering model selector."""
        from agento.ui.app import TUIApp

        app = TUIApp()
        table = app.render_model_selector()
        assert table is not None

    def test_update_state(self):
        """Test updating state."""
        from agento.core.state import AgentState, Message
        from agento.ui.app import TUIApp

        app = TUIApp()
        state = AgentState(
            messages=[Message(role="user", content="Hi")],
            model="openrouter/free",
        )

        app.update_state(state)

        assert app.state is state
        assert len(app.messages) == 1

    def test_get_help_text(self):
        """Test getting help text."""
        from agento.ui.app import TUIApp

        app = TUIApp()
        help_text = app._show_help()
        assert help_text is None


class TestUIModule:
    """Tests for UI module exports."""

    def test_import_console(self):
        """Test Console can be imported from ui."""
        from agento.ui.console import Console

        assert Console is not None

    def test_import_app(self):
        """Test TUIApp can be imported from ui."""
        from agento.ui.app import TUIApp

        assert TUIApp is not None

    def test_console_and_app_different(self):
        """Test Console and TUIApp are different classes."""
        from agento.ui.app import TUIApp
        from agento.ui.console import Console

        assert Console is not TUIApp
