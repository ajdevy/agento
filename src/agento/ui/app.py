"""TUI Application for Agento."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from rich.panel import Panel
from rich.table import Table

from agento.core.state import AgentState, Message
from agento.ui.console import Console as RichConsole


class TUIApp:
    """Terminal UI Application."""

    def __init__(
        self,
        on_message: Callable[[str], Awaitable[str]] | None = None,
    ):
        self.console = RichConsole()
        self.on_message = on_message
        self.messages: list[Message] = []
        self.state: AgentState | None = None
        self._running = False

    def render_header(self) -> Panel:
        """Render the header panel."""
        header_text = """
[bold magenta]AGENTO[/bold magenta] - AI Coding Assistant

Type your message and press Enter to chat.
Commands: /help, /clear, /model, /quit
        """
        return Panel(header_text.strip(), title="Welcome", border_style="blue")

    def render_messages(self) -> Panel:
        """Render the messages panel."""
        if not self.messages:
            content = "[dim]No messages yet. Start chatting![/dim]"
        else:
            lines = []
            for msg in self.messages[-10:]:
                role = msg.role.upper()
                color = (
                    "green"
                    if msg.role == "assistant"
                    else "yellow"
                    if msg.role == "user"
                    else "dim"
                )
                lines.append(f"[{color}]{role}[/{color}]: {msg.content[:200]}")

            content = "\n".join(lines) if lines else "[dim]No messages[/dim]"

        return Panel(content, title="Messages", border_style="green")

    def render_status(self) -> Panel:
        """Render the status panel."""
        if self.state is None:
            content = "[dim]Ready[/dim]"
        else:
            cost_str = (
                f"${self.state.cost_total:.4f}" if self.state.cost_total > 0 else "FREE"
            )
            content = f"Model: {self.state.model}\nCost: {cost_str}"

        return Panel(content, title="Status", border_style="yellow")

    def render_model_selector(self) -> Table:
        """Render model selection table."""
        table = Table(title="Available Models", show_header=True)
        table.add_column("Tier", style="cyan")
        table.add_column("Model", style="green")
        table.add_column("Cost", style="yellow")

        models = [
            ("Free", "openrouter/free", "$0.00"),
            ("Free (Code)", "qwen/qwen3-coder-480b-a35b:free", "$0.00"),
            ("Free (Reasoning)", "deepseek/deepseek-r1-0528:free", "$0.00"),
            ("Paid", "anthropic/claude-3.5-sonnet", "$3-15/M"),
        ]

        for tier, model, cost in models:
            table.add_row(tier, model, cost)

        return table

    def update_state(self, state: AgentState) -> None:
        """Update the agent state."""
        self.state = state
        self.messages = state.messages.copy()

    async def run(self) -> None:  # pragma: no cover
        """Run the TUI application."""  # pragma: no cover
        self._running = True

        self.console._console.print(self.render_header())
        self.console._console.print(self.render_model_selector())
        self.console.print("")

        while self._running:
            try:
                user_input = self.console.input("[bold cyan]You[/bold cyan]: ")

                if not user_input.strip():
                    continue

                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                else:
                    await self._handle_message(user_input)

            except (KeyboardInterrupt, EOFError):
                self._running = False
                self.console.print_success("Goodbye!")
                break

    async def _handle_command(self, command: str) -> None:  # pragma: no cover
        """Handle slash commands."""  # pragma: no cover
        cmd = command.lower().strip()

        if cmd in ("/quit", "/exit", "/q"):
            self._running = False
            self.console.print_success("Goodbye!")

        elif cmd == "/clear":
            self.console.clear()
            self.console.print(self.render_header())

        elif cmd == "/help":
            self._show_help()

        elif cmd == "/model":
            self.console.print(self.render_model_selector())

        elif cmd.startswith("/model "):
            model = cmd[7:].strip()
            self.console.print_info(f"Model set to: {model}")

        else:
            self.console.print_warning(f"Unknown command: {command}")
            self._show_help()

    async def _handle_message(self, message: str) -> None:  # pragma: no cover
        """Handle a user message."""  # pragma: no cover
        self.console.print_info("Thinking...")

        if self.on_message:
            response = await self.on_message(message)
            self.console.print_markdown(response)
        else:
            self.console.print_warning("No message handler configured")

    def _show_help(self) -> None:
        """Show help information."""
        help_text = """
**Available Commands:**

`/help` - Show this help
`/clear` - Clear the screen
`/model` - Show available models
`/model <name>` - Set the model
`/quit` - Exit the application
        """
        self.console.print_markdown(help_text)

    def stop(self) -> None:  # pragma: no cover
        """Stop the application."""  # pragma: no cover
        self._running = False  # pragma: no cover
