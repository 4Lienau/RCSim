#!/bin/bash
# Advanced Rubik's Cube Simulator - Development Environment Setup Script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python_version() {
    log_info "Checking Python version..."
    
    if ! command_exists python3; then
        log_error "Python 3 is not installed. Please install Python 3.9+ and try again."
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    required_version="3.9"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        log_error "Python $python_version found, but Python $required_version+ is required."
        exit 1
    fi
    
    log_success "Python $python_version found"
}

# Create virtual environment
create_virtual_env() {
    log_info "Setting up virtual environment..."
    
    if [ -d "venv" ]; then
        log_warning "Virtual environment already exists. Removing..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    log_success "Virtual environment created"
}

# Activate virtual environment and install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    python -m pip install --upgrade pip setuptools wheel
    
    # Install development dependencies
    pip install -r requirements-dev.txt
    
    # Install package in editable mode
    pip install -e .
    
    log_success "Dependencies installed"
}

# Install system dependencies (Linux)
install_system_deps_linux() {
    log_info "Installing system dependencies for Linux..."
    
    if command_exists apt-get; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y \
            libgl1-mesa-dev \
            libglu1-mesa-dev \
            libegl1-mesa-dev \
            libgles2-mesa-dev \
            libx11-dev \
            libxext-dev \
            libxrandr-dev \
            libxcursor-dev \
            libxinerama-dev \
            libxi-dev \
            libasound2-dev \
            libpulse-dev \
            xvfb
    elif command_exists yum; then
        # CentOS/RHEL/Fedora
        sudo yum install -y \
            mesa-libGL-devel \
            mesa-libGLU-devel \
            libX11-devel \
            libXext-devel \
            libXrandr-devel \
            libXcursor-devel \
            libXinerama-devel \
            libXi-devel \
            alsa-lib-devel \
            pulseaudio-libs-devel \
            xorg-x11-server-Xvfb
    elif command_exists pacman; then
        # Arch Linux
        sudo pacman -S --noconfirm \
            mesa \
            libgl \
            libx11 \
            libxext \
            libxrandr \
            libxcursor \
            libxinerama \
            libxi \
            alsa-lib \
            libpulse \
            xorg-server-xvfb
    else
        log_warning "Unknown package manager. Please install OpenGL and audio development libraries manually."
    fi
    
    log_success "System dependencies installed"
}

# Install system dependencies (macOS)
install_system_deps_macos() {
    log_info "Installing system dependencies for macOS..."
    
    if command_exists brew; then
        brew install \
            cmake \
            pkg-config
    else
        log_warning "Homebrew not found. Please install OpenGL development libraries manually."
    fi
    
    log_success "System dependencies installed"
}

# Install pre-commit hooks
setup_precommit() {
    log_info "Setting up pre-commit hooks..."
    
    source venv/bin/activate
    pre-commit install
    
    log_success "Pre-commit hooks installed"
}

# Create necessary directories
create_directories() {
    log_info "Creating project directories..."
    
    mkdir -p data logs config assets/textures assets/models assets/sounds
    
    log_success "Project directories created"
}

# Setup VS Code settings
setup_vscode() {
    if [ -d ".vscode" ]; then
        log_info "VS Code configuration already exists"
    else
        log_info "VS Code configuration not found. Please install the recommended extensions."
    fi
}

# Run initial tests
run_tests() {
    log_info "Running initial tests..."
    
    source venv/bin/activate
    
    # Run quick unit tests
    pytest tests/unit/ -x --tb=short
    
    log_success "Initial tests passed"
}

# Main setup function
main() {
    echo "🎮 Advanced Rubik's Cube Simulator - Development Setup"
    echo "===================================================="
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "pyproject.toml" ]; then
        log_error "Please run this script from the project root directory."
        exit 1
    fi
    
    # Detect OS and install system dependencies
    case "$(uname -s)" in
        Linux*)
            install_system_deps_linux
            ;;
        Darwin*)
            install_system_deps_macos
            ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*)
            log_warning "Windows detected. Please ensure you have Visual Studio Build Tools installed."
            ;;
        *)
            log_warning "Unknown operating system. You may need to install system dependencies manually."
            ;;
    esac
    
    # Python setup
    check_python_version
    create_virtual_env
    install_dependencies
    
    # Project setup
    setup_precommit
    create_directories
    setup_vscode
    
    # Verification
    run_tests
    
    echo ""
    echo "🎉 Development environment setup complete!"
    echo ""
    echo "To get started:"
    echo "  1. Activate the virtual environment: source venv/bin/activate"
    echo "  2. Run the application: python src/rcsim/main.py"
    echo "  3. Run tests: pytest tests/"
    echo "  4. Open in VS Code: code ."
    echo ""
    echo "For Docker development:"
    echo "  docker-compose up rcsim-dev"
    echo ""
    echo "Happy coding! 🚀"
}

# Run setup if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi