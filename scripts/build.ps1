# Agento Build Script for Windows (PowerShell)
# Usage: .\build.ps1 [options]

param(
    [switch]$Clean,
    [switch]$Dev,
    [switch]$Test,
    [switch]$Package,
    [switch]$Binary,
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# Configuration
$AppName = "agento"
$Version = (python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>$null) ?? "0.1.0"
$BuildDir = "dist"

# Colors
function Write-Info { param($m) Write-Host "ℹ $m" -ForegroundColor Cyan }
function Write-Success { param($m) Write-Host "✓ $m" -ForegroundColor Green }
function Write-Warning { param($m) Write-Host "⚠ $m" -ForegroundColor Yellow }
function Write-Err { param($m) Write-Host "✗ $m" -ForegroundColor Red }
function Write-Bold { param($m) Write-Host $m -ForegroundColor Magenta }

function Show-Help {
    Write-Host @"
Bold Usage:   .\build.ps1 [options]

Bold Options:
    -Clean       Remove build artifacts
    -Dev         Install in development mode
    -Test        Run tests after build
    -Package     Create distribution packages (sdist, wheel)
    -Binary      Create standalone binary (requires pyinstaller)
    -Install     Install globally
    -Uninstall   Uninstall globally
    -Help        Show this help

Bold Examples:
    .\build.ps1 -Dev          Install in dev mode
    .\build.ps1 -Package     Create distribution packages
    .\build.ps1 -Binary      Create standalone binary
    .\build.ps1 -Install     Install globally
"@
}

# Check prerequisites
function Check-Prereqs {
    Write-Info "Checking prerequisites..."

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Err "Python 3 is required but not found"
        exit 1
    }

    $pyVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    Write-Success "Prerequisites OK (Python $pyVersion)"
}

# Create virtual environment
function Setup-Venv {
    Write-Info "Setting up virtual environment..."

    if (-not (Test-Path ".venv")) {
        python -m venv .venv
        Write-Success "Virtual environment created"
    } else {
        Write-Success "Virtual environment already exists"
    }

    & .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip --quiet
}

# Install dependencies
function Install-Deps {
    Write-Info "Installing dependencies..."
    pip install -e ".[all]" --quiet
    Write-Success "Dependencies installed"
}

# Run tests
function Run-Tests {
    Write-Info "Running tests..."
    pytest tests/ --timeout=30 -q --tb=short
    Write-Success "Tests passed"
}

# Build distribution packages
function Build-Packages {
    Write-Info "Building distribution packages..."

    New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

    Write-Info "Building wheel..."
    python -m build --wheel

    Write-Info "Building source distribution..."
    python -m build --sdist

    Write-Success "Packages created:"
    Get-ChildItem "$BuildDir\*.whl", "$BuildDir\*.tar.gz" | ForEach-Object {
        Write-Host "  $($_.Name) ($('{0:N2}' -f ($_.Length / 1MB)) MB)"
    }
}

# Build binary with PyInstaller
function Build-Binary {
    Write-Info "Building standalone binary..."

    if (-not (pip show pyinstaller 2>$null)) {
        Write-Info "Installing PyInstaller..."
        pip install pyinstaller --quiet
    }

    New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

    Remove-Item "$BuildDir\$AppName.exe" -Force -ErrorAction SilentlyContinue

    pyinstaller --name=$AppName --onefile --console --clean src/agento/main.py

    if (Test-Path "dist\$AppName.exe") {
        Write-Success "Binary created: dist\$AppName.exe"
        $size = (Get-Item "dist\$AppName.exe").Length / 1MB
        Write-Info "Size: $([math]::Round($size, 2)) MB"
    } else {
        Write-Err "Binary build failed"
        exit 1
    }
}

# Install globally
function Install-Global {
    Write-Info "Installing $AppName v$Version globally..."
    pip install -e .
    Write-Success "Installed! Run 'agento --help' to get started"
}

# Uninstall globally
function Uninstall-Global {
    Write-Info "Uninstalling $AppName globally..."
    pip uninstall $AppName -y 2>$null
    Write-Success "Uninstalled"
}

# Clean
function Clean {
    Write-Info "Cleaning build artifacts..."
    Remove-Item -Recurse -Force "build", "dist", "*.egg-info", ".pytest_cache" -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Directory "**/__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Include "*.pyc","*.pyo" | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Success "Clean complete"
}

# Main
function Main {
    Write-Host ""
    Write-Bold "========================================="
    Write-Bold "  $AppName Build Script v$Version"
    Write-Bold "========================================="
    Write-Host ""

    if ($Help) {
        Show-Help
        return
    }

    if ($Uninstall) {
        Uninstall-Global
        return
    }

    if ($Install) {
        Install-Global
        return
    }

    if ($Clean) {
        Clean
    }

    Check-Prereqs
    Setup-Venv
    Install-Deps

    if ($Dev) {
        Write-Success "Development mode ready!"
        Write-Info "Activate with: .\.venv\Scripts\Activate.ps1"
        Write-Info "Run agento: agento"
        return
    }

    if ($Test) {
        Run-Tests
    }

    if ($Package) {
        Build-Packages
    }

    if ($Binary) {
        Build-Binary
    }

    if (-not $Package -and -not $Binary -and -not $Test) {
        Write-Success "Development mode ready!"
        Write-Info "Activate with: .\.venv\Scripts\Activate.ps1"
        Write-Info "Run agento: agento"
        Write-Host ""
        Write-Info "Other options:"
        Write-Info "  -Test    Run tests"
        Write-Info "  -Package Create distribution packages"
        Write-Info "  -Binary  Create standalone binary"
        Write-Info "  -Install Install globally"
    }

    Write-Host ""
    Write-Success "Done!"
}

Main
