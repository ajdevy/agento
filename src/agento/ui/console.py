"""Rich console for terminal output."""

from __future__ import annotations

from typing import Any

from rich.console import Console as RichConsole
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table


class Console:
    """Rich console wrapper for terminal output."""

    def __init__(self) -> None:
        self._console = RichConsole()

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print to console."""
        self._console.print(*args, **kwargs)

    def print_markdown(self, text: str) -> None:
        """Print markdown text."""
        md = Markdown(text)
        self._console.print(md)

    def print_code(self, code: str, language: str = "python") -> None:
        """Print syntax-highlighted code."""
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self._console.print(syntax)

    def print_panel(self, content: str, title: str = "") -> None:
        """Print in a panel."""
        panel = Panel(content, title=title)
        self._console.print(panel)

    def print_table(self, data: list[dict[str, Any]], title: str = "") -> None:
        """Print a table."""
        if not data:
            return

        table = Table(title=title, show_header=True, header_style="bold magenta")
        headers = list(data[0].keys())

        for header in headers:
            table.add_column(header)

        for row in data:
            table.add_row(*[str(row.get(h, "")) for h in headers])

        self._console.print(table)

    def print_info(self, message: str) -> None:
        """Print info message."""
        self._console.print(f"[blue]i[/blue] {message}")

    def print_success(self, message: str) -> None:
        """Print success message."""
        self._console.print(f"[green]✓[/green] {message}")

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        self._console.print(f"[yellow]⚠[/yellow] {message}")

    def print_error(self, message: str) -> None:
        """Print error message."""
        self._console.print(f"[red]✗[/red] {message}")

    def print_model_info(self, model: str, cost: float, tokens: int) -> None:
        """Print model usage info."""
        cost_str = f"${cost:.4f}" if cost > 0 else "FREE"
        self._console.print(
            f"[dim]Model: {model} | Tokens: {tokens} | Cost: {cost_str}[/dim]"
        )

    def print_cost_preview(self, model: str, estimated_cost: float) -> None:
        """Print cost preview before request."""
        cost_str = f"${estimated_cost:.4f}" if estimated_cost > 0 else "FREE"
        self._console.print(f"[dim]Estimated cost: {cost_str}[/dim]")

    def input(self, prompt: str = "> ", mode: str = "chat") -> str:
        """Get input from user."""
        mode_prompt = f"[yellow]{mode}[/yellow]> "
        return self._console.input(mode_prompt)

    def clear(self) -> None:
        """Clear the console."""
        self._console.clear()

    def print_banner(self) -> None:
        """Print the application banner."""
        banner = """
[bold magenta]╔══════════════════════════════════════════════════════════════╗[/bold magenta]
[bold magenta]║[/bold magenta]  [bold cyan]AGENTO[/bold cyan] - AI Coding Assistant                              [bold magenta]║[/bold magenta]
[bold magenta]║[/bold magenta]  [dim]Your intelligent coding companion[/dim]                          [bold magenta]║[/bold magenta]
[bold magenta]╚══════════════════════════════════════════════════════════════╝[/bold magenta]
        """
        self._console.print(banner)

    def print_help_hint(self) -> None:
        """Print hint about getting API key."""
        self._console.print(
            "[dim]Get your free API key at: https://openrouter.ai/keys[/dim]"
        )


console = Console()
