#!/usr/bin/env python3
"""Build script for agento - works on Mac, Linux, and Windows."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a command."""
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, **kwargs)


def info(msg: str) -> None:
    """Print info message."""
    print(f"  → {msg}")


def success(msg: str) -> None:
    """Print success message."""
    print(f"  ✓ {msg}")


def error(msg: str) -> None:
    """Print error message."""
    print(f"  ✗ {msg}")


def main() -> None:
    """Main build function."""
    print("=" * 50)
    print("  Agento Build Script")
    print("=" * 50)
    print()

    args = sys.argv[1:]

    # Help
    if "--help" in args or "-h" in args:
        print("Usage: python build.py [options]")
        print()
        print("Options:")
        print("  --clean      Clean build artifacts")
        print("  --dev        Install in development mode")
        print("  --test       Run tests")
        print("  --package    Build distribution packages")
        print("  --binary     Build standalone binary (requires pyinstaller)")
        print("  --install    Install globally")
        print()
        return

    # Clean
    if "--clean" in args:
        info("Cleaning build artifacts...")
        dirs_to_remove = ["build", "dist", "*.egg-info", ".pytest_cache", ".venv"]
        for d in dirs_to_remove:
            if Path(d).exists():
                if d.endswith("*"):
                    for item in Path(".").glob(d):
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                else:
                    if Path(d).is_dir():
                        shutil.rmtree(d)
                    else:
                        Path(d).unlink()
        success("Clean complete")
        print()
        return

    # Ensure we're in a venv
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        info("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        venv_python = (
            ".venv/bin/python" if os.name != "nt" else ".venv\\Scripts\\python.exe"
        )
        subprocess.run([venv_python, __file__] + args, check=True)
        return

    # Upgrade pip
    info("Upgrading pip...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True
    )

    # Dev install
    if (
        "--dev" in args
        or "--install" not in args
        and "--package" not in args
        and "--binary" not in args
    ):
        info("Installing in development mode...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", ".[all]"],
            check=True,
        )
        success("Development mode ready!")
        print()
        info("Activate with: source .venv/bin/activate")
        info("Run agento: agento run")
        print()
        return

    # Test
    if "--test" in args:
        info("Running tests...")
        subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "--timeout=30", "-q"],
            check=False,  # Don't fail on test errors
        )
        success("Tests complete")
        print()

    # Install
    if "--install" in args:
        info("Installing globally...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
        success("Installed! Run 'agento --help' to get started")
        print()
        return

    # Package
    if "--package" in args:
        info("Building distribution packages...")
        os.makedirs("dist", exist_ok=True)
        subprocess.run([sys.executable, "-m", "build", "--sdist"], check=True)
        subprocess.run([sys.executable, "-m", "build", "--wheel"], check=True)
        success("Packages created in dist/")
        print()

    # Binary
    if "--binary" in args:
        info("Building standalone binary...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"], check=True
        )
        os.makedirs("dist", exist_ok=True)
        binary = "dist/agento.exe" if os.name == "nt" else "dist/agento"
        if Path(binary).exists():
            Path(binary).unlink()
        subprocess.run(
            [
                sys.executable,
                "-m",
                "PyInstaller",
                "--name=agento",
                "--onefile",
                "--console",
                "--clean",
                "src/agento/main.py",
            ],
            check=True,
        )
        success(f"Binary created: {binary}")
        print()

    print("Done!")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        error(f"Command failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
