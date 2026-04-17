"""Agento main entry point."""

from __future__ import annotations

import asyncio

import typer

from agento.application.pipeline import Pipeline, PipelineConfig
from agento.config import settings
from agento.ui.console import console

app = typer.Typer(help="Agento - AI Coding Assistant")


def check_api_key() -> str | None:
    """Check for API key and return it."""
    if (
        settings.openrouter_api_key and settings.openrouter_api_key.get_secret_value()
    ):  # pragma: no cover
        return settings.openrouter_api_key.get_secret_value()  # pragma: no cover
    if (
        settings.deepseek_api_key and settings.deepseek_api_key.get_secret_value()
    ):  # pragma: no cover
        return settings.deepseek_api_key.get_secret_value()  # pragma: no cover
    if (
        settings.google_api_key and settings.google_api_key.get_secret_value()
    ):  # pragma: no cover
        return settings.google_api_key.get_secret_value()  # pragma: no cover
    return None


@app.command()
def run(  # pragma: no cover
    model: str = typer.Option(None, "--model", "-m", help="Model to use"),
    show_cost: bool = typer.Option(
        True, "--show-cost/--no-cost", help="Show cost preview"
    ),
    show_model: bool = typer.Option(
        True, "--show-model/--no-model", help="Show model info"
    ),
) -> None:  # pragma: no cover
    """Run the Agento agent."""  # pragma: no cover
    console.print("Agento v0.1.0")
    console.print("=" * 50)

    api_key = check_api_key()
    if not api_key:
        console.print_error("No API key configured!")
        console.print("Please set one of:")
        console.print("  - OPENROUTER_API_KEY")
        console.print("  - DEEPSEEK_API_KEY")
        console.print("  - GOOGLE_API_KEY")
        console.print("\nCreate a .env file or export the API key.")
        raise typer.Exit(code=1)

    config = PipelineConfig(
        model=model or settings.default_model,
        show_cost=show_cost,
        show_model=show_model,
    )

    async def main() -> None:
        async with Pipeline(api_key=api_key, config=config) as pipeline:
            await pipeline.run()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print_success("\nGoodbye!")
    except Exception as e:
        console.print_error(f"Error: {e!s}")
        msg = e
        raise typer.Exit(code=1) from msg


@app.command()
def chat(  # pragma: no cover
    message: str = typer.Argument(..., help="Message to send"),
    model: str = typer.Option(None, "--model", "-m", help="Model to use"),
) -> None:  # pragma: no cover
    """Send a single chat message."""  # pragma: no cover
    api_key = check_api_key()
    if not api_key:
        console.print_error("No API key configured!")
        raise typer.Exit(code=1)

    config = PipelineConfig(model=model or settings.default_model)

    async def main() -> None:
        async with Pipeline(api_key=api_key, config=config) as pipeline:
            response = await pipeline.chat(message)
            console.print_markdown(response)

    asyncio.run(main())


@app.command()
def models() -> None:  # pragma: no cover
    """List available models."""  # pragma: no cover
    from agento.infrastructure.llm.router import MODEL_ROUTING  # pragma: no cover

    console.print_panel("Available Models", title="Agento")  # pragma: no cover

    for task_type, routing in MODEL_ROUTING.items():  # pragma: no cover
        console.print(f"\n[bold]{task_type.upper()}:[/bold]")  # pragma: no cover
        console.print(f"  Free:     {routing.free}")  # pragma: no cover
        console.print(f"  Primary:  {routing.primary}")  # pragma: no cover
        console.print(f"  Fallback: {routing.fallback}")  # pragma: no cover


@app.command()
def version() -> None:  # pragma: no cover
    """Show version information."""  # pragma: no cover
    console.print("Agento v0.1.0")  # pragma: no cover


def cli() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    cli()
