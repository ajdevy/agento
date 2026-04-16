"""Agento main entry point."""

from __future__ import annotations

import sys


def run() -> None:
    """Run the Agento agent."""
    print("Agento v0.1.0")
    print("=" * 50)
    print("Initializing...")

    try:
        from agento.config import settings

        if not settings.has_api_key:
            print("ERROR: No API key configured!")
            print("Please set one of:")
            print("  - OPENROUTER_API_KEY")
            print("  - DEEPSEEK_API_KEY")
            print("  - GOOGLE_API_KEY")
            print("\nCreate a .env file or export the API key.")
            sys.exit(1)

        print("Configuration loaded successfully!")
        print(f"Default model: {settings.default_model}")
        print("\nAgent initialization complete!")
        print("\nTo run the full agent, complete Phase 1 implementation.")
        print("See PLAN/PHASE-01.md for details.")

    except ImportError as e:
        print(f"ERROR: Missing dependencies: {e}")
        print("Run: pip install -e .")
        sys.exit(1)


if __name__ == "__main__":
    run()
