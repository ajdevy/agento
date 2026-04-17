#!/bin/bash
# Cross-platform build script for agento CLI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

BOLD='\033[1m'

# Configuration
APP_NAME="agento"
VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || echo "0.1.0")
BUILD_DIR="dist"

# Print functions
info() { echo -e "${BLUE}ℹ${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warning() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }

bold() { echo -e "${BOLD}$1${NC}"; }

# Help
show_help() {
    cat << EOF
${BOLD}Usage:${NC} ./build.sh [options]

${BOLD}Options:${NC}
    --clean          Remove build artifacts
    --dev           Install in development mode
    --test          Run tests after build
    --package       Create distribution packages (sdist, wheel)
    --binary        Create standalone binary (requires pyinstaller)
    --install       Install globally (requires sudo on Linux)
    --uninstall     Uninstall globally (requires sudo on Linux)
    --help          Show this help

${BOLD}Examples:${NC}
    ./build.sh --dev          # Install in dev mode
    ./build.sh --package      # Create distribution packages
    ./build.sh --binary       # Create standalone binary
    ./build.sh --install      # Install globally (Linux)
    sudo ./build.sh --install # Install globally (Linux with sudo)

EOF
}

# Check prerequisites
check_prereqs() {
    info "Checking prerequisites..."

    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not found"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ $(echo "$PYTHON_VERSION < 3.11" | bc) -eq 1 ]]; then
        warning "Python $PYTHON_VERSION detected. Python 3.11+ is recommended"
    fi

    success "Prerequisites OK (Python $PYTHON_VERSION)"
}

# Create virtual environment
setup_venv() {
    info "Setting up virtual environment..."

    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        success "Virtual environment created"
    else
        success "Virtual environment already exists"
    fi

    source .venv/bin/activate

    info "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1
}

# Install dependencies
install_deps() {
    info "Installing dependencies..."
    pip install -e ".[all]" --quiet
    success "Dependencies installed"
}

# Run tests
run_tests() {
    info "Running tests..."
    pytest tests/ --timeout=30 -q --tb=short
    success "Tests passed"
}

# Build distribution packages
build_packages() {
    info "Building distribution packages..."

    mkdir -p "$BUILD_DIR"

    # Build wheel
    info "Building wheel..."
    python3 -m build --wheel

    # Build sdist
    info "Building source distribution..."
    python3 -m build --sdist

    success "Packages created:"
    ls -lh "$BUILD_DIR"/*.whl "$BUILD_DIR"/*.tar.gz 2>/dev/null | awk '{print "  " $9 " (" $5 ")" }'
}

# Build binary with PyInstaller
build_binary() {
    info "Building standalone binary..."

    if ! pip show pyinstaller > /dev/null 2>&1; then
        info "Installing PyInstaller..."
        pip install pyinstaller --quiet
    fi

    mkdir -p "$BUILD_DIR"

    # Remove old binary
    rm -f "$BUILD_DIR/$APP_NAME" 2>/dev/null || true

    pyinstaller --name="$APP_NAME" \
        --onefile \
        --console \
        --clean \
        --additional-hooks-dir="" \
        src/agento/main.py \
        2>/dev/null

    if [ -f "dist/$APP_NAME" ]; then
        chmod +x "dist/$APP_NAME"
        success "Binary created: dist/$APP_NAME"
        info "Size: $(du -h dist/$APP_NAME | cut -f1)"
    else
        error "Binary build failed"
        exit 1
    fi
}

# Install globally (Linux/macOS)
install_global() {
    info "Installing $APP_NAME v$VERSION globally..."

    # Try pipx first (preferred)
    if command -v pipx &> /dev/null; then
        info "Installing via pipx..."
        pipx install -e .
        success "Installed via pipx"
        return
    fi

    # Fall back to pip with --user
    info "Installing via pip (user mode)..."
    pip install -e . --user

    # Add to PATH if needed
    USER_BIN=$(python3 -c "import site; print(site.getuserbase() + '/bin')")
    if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
        warning "Add this to your PATH if not already present:"
        echo "  export PATH=\"\$PATH:$USER_BIN\""
    fi

    success "Installed! Run 'agento --help' to get started"
}

# Uninstall globally
uninstall_global() {
    info "Uninstalling $APP_NAME globally..."

    if command -v pipx &> /dev/null; then
        pipx uninstall agento 2>/dev/null || true
    fi

    pip uninstall agento -y 2>/dev/null || true

    success "Uninstalled"
}

# Clean build artifacts
clean() {
    info "Cleaning build artifacts..."
    rm -rf build/ dist/ *.egg-info .pytest_cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    success "Clean complete"
}

# Main
main() {
    bold "========================================="
    bold "  $APP_NAME Build Script v$VERSION"
    bold "========================================="
    echo ""

    # Parse options
    CLEAN=false
    DEV=false
    TEST=false
    PACKAGE=false
    BINARY=false
    INSTALL=false
    UNINSTALL=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean) CLEAN=true; shift ;;
            --dev) DEV=true; shift ;;
            --test) TEST=true; shift ;;
            --package) PACKAGE=true; shift ;;
            --binary) BINARY=true; shift ;;
            --install) INSTALL=true; shift ;;
            --uninstall) UNINSTALL=true; shift ;;
            --help) show_help; exit 0 ;;
            *) error "Unknown option: $1"; show_help; exit 1 ;;
        esac
    done

    # Handle commands
    if [ "$CLEAN" = true ]; then
        clean
    fi

    if [ "$UNINSTALL" = true ]; then
        uninstall_global
        exit 0
    fi

    if [ "$INSTALL" = true ]; then
        install_global
        exit 0
    fi

    # Build steps
    check_prereqs
    setup_venv
    install_deps

    if [ "$DEV" = true ]; then
        success "Development mode ready!"
        info "Activate with: source .venv/bin/activate"
        info "Run agento: agento"
        exit 0
    fi

    if [ "$TEST" = true ]; then
        run_tests
    fi

    if [ "$PACKAGE" = true ]; then
        build_packages
    fi

    if [ "$BINARY" = true ]; then
        build_binary
    fi

    if [ "$PACKAGE" = false ] && [ "$BINARY" = false ] && [ "$TEST" = false ]; then
        success "Development mode ready!"
        info "Activate with: source .venv/bin/activate"
        info "Run agento: agento"
        info ""
        info "Other options:"
        info "  --test    Run tests"
        info "  --package Create distribution packages"
        info "  --binary Create standalone binary"
        info "  --install Install globally"
    fi

    echo ""
    success "Done!"
}

main "$@"
