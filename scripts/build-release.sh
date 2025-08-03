#!/bin/bash
# Advanced Rubik's Cube Simulator - Release Build Script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
VERSION=""
CLEAN=true
TESTS=true
DOCS=true
DOCKER=false
UPLOAD=false
DRY_RUN=false

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Release build script for Advanced Rubik's Cube Simulator"
    echo ""
    echo "Options:"
    echo "  -v, --version VERSION Version to build (required)"
    echo "  --no-clean           Skip cleaning build artifacts"
    echo "  --no-tests           Skip running tests"
    echo "  --no-docs            Skip building documentation"
    echo "  -d, --docker         Build Docker images"
    echo "  -u, --upload         Upload to PyPI (requires credentials)"
    echo "  --dry-run            Dry run - don't actually build/upload"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -v 1.0.0          # Build version 1.0.0"
    echo "  $0 -v 1.0.0 -d       # Build with Docker images"
    echo "  $0 -v 1.0.0 -u       # Build and upload to PyPI"
}

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

# Validate version format
validate_version() {
    if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$ ]]; then
        log_error "Invalid version format: $VERSION"
        log_error "Expected format: X.Y.Z or X.Y.Z-suffix (e.g., 1.0.0, 1.0.0-beta1)"
        exit 1
    fi
    
    log_info "Building version: $VERSION"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]]; then
        log_error "Please run this script from the project root directory."
        exit 1
    fi
    
    # Check if virtual environment is activated
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        log_warning "Virtual environment not detected. Attempting to activate..."
        if [[ -f "venv/bin/activate" ]]; then
            source venv/bin/activate
            log_info "Virtual environment activated"
        else
            log_error "Virtual environment not found. Please run setup-dev.sh first."
            exit 1
        fi
    fi
    
    # Check required tools
    local required_tools=("python" "pip" "git")
    for tool in "${required_tools[@]}"; do
        if ! command_exists "$tool"; then
            log_error "Required tool not found: $tool"
            exit 1
        fi
    done
    
    # Check for build dependencies
    python -c "import build, twine" 2>/dev/null || {
        log_info "Installing build dependencies..."
        pip install build twine
    }
    
    log_success "Prerequisites checked"
}

# Clean build artifacts
clean_build() {
    if [[ "$CLEAN" == true ]]; then
        log_info "Cleaning build artifacts..."
        
        rm -rf build/
        rm -rf dist/
        rm -rf src/*.egg-info/
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        
        log_success "Build artifacts cleaned"
    fi
}

# Update version in files
update_version() {
    log_info "Updating version in project files..."
    
    if [[ "$DRY_RUN" == false ]]; then
        # Update pyproject.toml
        sed -i.bak "s/^version = .*/version = \"$VERSION\"/" pyproject.toml
        
        # Update __init__.py
        if [[ -f "src/rcsim/__init__.py" ]]; then
            sed -i.bak "s/__version__ = .*/__version__ = \"$VERSION\"/" src/rcsim/__init__.py
        fi
        
        # Clean up backup files
        find . -name "*.bak" -delete 2>/dev/null || true
    fi
    
    log_success "Version updated to $VERSION"
}

# Run tests
run_tests() {
    if [[ "$TESTS" == true ]]; then
        log_info "Running test suite..."
        
        if [[ "$DRY_RUN" == false ]]; then
            # Run the test script
            ./scripts/run-tests.sh --type all --coverage
        else
            log_info "[DRY RUN] Would run: ./scripts/run-tests.sh --type all --coverage"
        fi
        
        log_success "Tests completed"
    fi
}

# Build documentation
build_docs() {
    if [[ "$DOCS" == true ]]; then
        log_info "Building documentation..."
        
        if [[ "$DRY_RUN" == false ]]; then
            if [[ -d "docs" ]]; then
                cd docs
                make clean
                make html
                cd ..
            else
                log_warning "Documentation directory not found, skipping docs build"
            fi
        else
            log_info "[DRY RUN] Would build documentation"
        fi
        
        log_success "Documentation built"
    fi
}

# Build Python package
build_package() {
    log_info "Building Python package..."
    
    if [[ "$DRY_RUN" == false ]]; then
        # Build source distribution and wheel
        python -m build
        
        # Check the distribution
        twine check dist/*
    else
        log_info "[DRY RUN] Would run: python -m build"
    fi
    
    log_success "Package built"
}

# Build Docker images
build_docker() {
    if [[ "$DOCKER" == true ]]; then
        log_info "Building Docker images..."
        
        if ! command_exists docker; then
            log_error "Docker not found. Please install Docker to build images."
            exit 1
        fi
        
        if [[ "$DRY_RUN" == false ]]; then
            # Build production image
            docker build -t "rcsim:$VERSION" -t "rcsim:latest" \
                --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
                --build-arg VCS_REF="$(git rev-parse HEAD)" \
                --build-arg VERSION="$VERSION" \
                .
            
            # Build development image
            docker build -f Dockerfile.dev -t "rcsim:$VERSION-dev" -t "rcsim:dev" .
        else
            log_info "[DRY RUN] Would build Docker images"
        fi
        
        log_success "Docker images built"
    fi
}

# Create git tag
create_git_tag() {
    log_info "Creating git tag..."
    
    if [[ "$DRY_RUN" == false ]]; then
        # Check if tag already exists
        if git tag -l "v$VERSION" | grep -q "v$VERSION"; then
            log_warning "Tag v$VERSION already exists"
        else
            git tag -a "v$VERSION" -m "Release version $VERSION"
            log_success "Git tag v$VERSION created"
        fi
    else
        log_info "[DRY RUN] Would create git tag: v$VERSION"
    fi
}

# Upload to PyPI
upload_to_pypi() {
    if [[ "$UPLOAD" == true ]]; then
        log_info "Uploading to PyPI..."
        
        if [[ "$DRY_RUN" == false ]]; then
            # Check if PYPI_API_TOKEN is set
            if [[ -z "${PYPI_API_TOKEN:-}" ]]; then
                log_warning "PYPI_API_TOKEN not set. Using interactive authentication."
                twine upload dist/*
            else
                twine upload --username __token__ --password "$PYPI_API_TOKEN" dist/*
            fi
        else
            log_info "[DRY RUN] Would upload to PyPI"
        fi
        
        log_success "Package uploaded to PyPI"
    fi
}

# Generate release notes
generate_release_notes() {
    log_info "Generating release notes..."
    
    local release_notes_file="RELEASE_NOTES_v$VERSION.md"
    
    if [[ "$DRY_RUN" == false ]]; then
        cat > "$release_notes_file" << EOF
# Release Notes - Version $VERSION

## What's New

<!-- Add release highlights here -->

## Changes

$(git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || echo "")..HEAD 2>/dev/null || echo "Initial release")

## Installation

\`\`\`bash
pip install rcsim==$VERSION
\`\`\`

## Docker

\`\`\`bash
docker pull rcsim:$VERSION
\`\`\`

## Files

- Source distribution: \`rcsim-$VERSION.tar.gz\`
- Wheel distribution: \`rcsim-$VERSION-py3-none-any.whl\`

---

Built on $(date)
EOF
    else
        log_info "[DRY RUN] Would generate: $release_notes_file"
    fi
    
    log_success "Release notes generated: $release_notes_file"
}

# Main function
main() {
    echo "🚀 Advanced Rubik's Cube Simulator - Release Builder"
    echo "=================================================="
    echo ""
    
    if [[ -z "$VERSION" ]]; then
        log_error "Version is required. Use -v or --version to specify."
        usage
        exit 1
    fi
    
    validate_version
    check_prerequisites
    
    if [[ "$DRY_RUN" == true ]]; then
        log_warning "DRY RUN MODE - No actual changes will be made"
        echo ""
    fi
    
    # Build process
    clean_build
    update_version
    run_tests
    build_docs
    build_package
    build_docker
    create_git_tag
    generate_release_notes
    upload_to_pypi
    
    echo ""
    log_success "Release build completed for version $VERSION!"
    echo ""
    
    if [[ "$DRY_RUN" == false ]]; then
        echo "📦 Built packages:"
        ls -la dist/ 2>/dev/null || true
        echo ""
        
        if [[ "$DOCKER" == true ]]; then
            echo "🐳 Docker images:"
            docker images rcsim 2>/dev/null || true
            echo ""
        fi
        
        echo "Next steps:"
        echo "  1. Review the built packages in dist/"
        echo "  2. Test the release in a clean environment"
        echo "  3. Push the git tag: git push origin v$VERSION"
        if [[ "$UPLOAD" != true ]]; then
            echo "  4. Upload to PyPI: twine upload dist/*"
        fi
        echo "  5. Create GitHub release with release notes"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        --no-clean)
            CLEAN=false
            shift
            ;;
        --no-tests)
            TESTS=false
            shift
            ;;
        --no-docs)
            DOCS=false
            shift
            ;;
        -d|--docker)
            DOCKER=true
            shift
            ;;
        -u|--upload)
            UPLOAD=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi