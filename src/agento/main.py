"""Agento main entry point - TUI Interface."""

from __future__ import annotations

import asyncio
import sys

from agento.config import settings
from agento.ui.console import console


def check_api_key() -> str | None:
    """Check for API key and return it."""
    if settings.openrouter_api_key and settings.openrouter_api_key.get_secret_value():
        return settings.openrouter_api_key.get_secret_value()
    if settings.deepseek_api_key and settings.deepseek_api_key.get_secret_value():
        return settings.deepseek_api_key.get_secret_value()
    if settings.google_api_key and settings.google_api_key.get_secret_value():
        return settings.google_api_key.get_secret_value()
    return None


async def run_tui(model: str | None = None) -> None:
    """Run the interactive TUI."""
    from agento.application.pipeline import Pipeline, PipelineConfig

    api_key = check_api_key()
    if not api_key:
        console.print_error("No API key configured!")
        console.print("")
        console.print("Choose a provider:")
        console.print("  1. OpenRouter (recommended - free models at openrouter.ai)")
        console.print("  2. DeepSeek")
        console.print("  3. Google AI (Gemini)")
        console.print("")
        choice = console._console.input("Enter provider (1/2/3): ").strip()

        if choice == "1":
            console.print("Get your free API key from https://openrouter.ai/keys")
            key_input = console._console.input("Enter OPENROUTER_API_KEY: ").strip()
            if key_input:
                api_key = key_input
            else:
                console.print_error("No API key provided. Exiting.")
                sys.exit(1)
        elif choice == "2":
            console.print("Get API key from https://platform.deepseek.com/")
            key_input = console._console.input("Enter DEEPSEEK_API_KEY: ").strip()
            if key_input:
                api_key = key_input
            else:
                console.print_error("No API key provided. Exiting.")
                sys.exit(1)
        elif choice == "3":
            console.print("Get API key from https://aistudio.google.com/")
            key_input = console._console.input("Enter GOOGLE_API_KEY: ").strip()
            if key_input:
                api_key = key_input
            else:
                console.print_error("No API key provided. Exiting.")
                sys.exit(1)
        else:
            console.print_error("Invalid choice. Exiting.")
            sys.exit(1)

    config = PipelineConfig(model=model or settings.default_model)

    try:
        async with Pipeline(api_key=api_key, config=config) as pipeline:
            await pipeline.run()
    except KeyboardInterrupt:
        console.print_success("\nGoodbye!")
    except Exception as e:
        console.print_error(f"Error: {e!s}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    console.print_banner()

    import argparse

    parser = argparse.ArgumentParser(
        prog="agento",
        description="Agento - AI Coding Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default=None,
        help="Model to use (e.g., openrouter/free, anthropic/claude-3.5-sonnet)",
    )
    parser.add_argument(
        "--no-cost",
        action="store_true",
        help="Hide cost preview",
    )
    parser.add_argument(
        "--no-model",
        action="store_true",
        help="Hide model info",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Agento v0.1.0",
    )

    args = parser.parse_args()

    config_overrides = {}
    if args.no_cost:
        config_overrides["show_cost"] = False
    if args.no_model:
        config_overrides["show_model"] = False

    asyncio.run(run_tui(model=args.model))


if __name__ == "__main__":
    main()
