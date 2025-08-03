#!/bin/bash
# Advanced Rubik's Cube Simulator - Repository Synchronization Script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
REPO_URL=""
BRANCH="main"
SETUP_REMOTE=true
INITIAL_COMMIT=true
PUSH_TO_REMOTE=true
FORCE_PUSH=false

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS] <REPOSITORY_URL>"
    echo ""
    echo "Repository synchronization script for Advanced Rubik's Cube Simulator"
    echo ""
    echo "Arguments:"
    echo "  REPOSITORY_URL    GitHub repository URL (e.g., https://github.com/user/repo.git)"
    echo ""
    echo "Options:"
    echo "  -b, --branch BRANCH      Branch name (default: main)"
    echo "  --no-setup-remote        Skip setting up remote origin"
    echo "  --no-initial-commit      Skip creating initial commit"
    echo "  --no-push               Skip pushing to remote"
    echo "  -f, --force-push        Force push to remote (use with caution)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 https://github.com/user/rubiks-cube-sim.git"
    echo "  $0 -b develop --no-push https://github.com/user/rubiks-cube-sim.git"
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if we're in the right directory
    if [[ ! -f "pyproject.toml" ]]; then
        log_error "Please run this script from the project root directory."
        exit 1
    fi
    
    # Check for git
    if ! command_exists git; then
        log_error "Git is not installed. Please install Git and try again."
        exit 1
    fi
    
    # Check if git is initialized
    if [[ ! -d ".git" ]]; then
        log_info "Git repository not initialized. Initializing..."
        git init
        log_success "Git repository initialized"
    fi
    
    log_success "Prerequisites checked"
}

# Validate repository URL
validate_repo_url() {
    if [[ -z "$REPO_URL" ]]; then
        log_error "Repository URL is required."
        usage
        exit 1
    fi
    
    # Basic URL validation
    if [[ ! "$REPO_URL" =~ ^https://github\.com/.+/.+\.git$ ]] && 
       [[ ! "$REPO_URL" =~ ^git@github\.com:.+/.+\.git$ ]]; then
        log_warning "Repository URL doesn't match expected GitHub format"
        log_warning "Expected: https://github.com/user/repo.git or git@github.com:user/repo.git"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_info "Repository URL: $REPO_URL"
}

# Setup git configuration
setup_git_config() {
    log_info "Setting up git configuration..."
    
    # Check if user name and email are configured
    if ! git config user.name >/dev/null 2>&1; then
        log_warning "Git user.name not configured"
        read -p "Enter your name: " git_name
        git config user.name "$git_name"
    fi
    
    if ! git config user.email >/dev/null 2>&1; then
        log_warning "Git user.email not configured"
        read -p "Enter your email: " git_email
        git config user.email "$git_email"
    fi
    
    # Set up useful git configuration
    git config init.defaultBranch "$BRANCH"
    git config pull.rebase false
    git config push.default simple
    
    log_success "Git configuration updated"
}

# Setup remote origin
setup_remote() {
    if [[ "$SETUP_REMOTE" == true ]]; then
        log_info "Setting up remote origin..."
        
        # Check if remote origin already exists
        if git remote get-url origin >/dev/null 2>&1; then
            existing_url=$(git remote get-url origin)
            if [[ "$existing_url" != "$REPO_URL" ]]; then
                log_warning "Remote origin already exists with different URL: $existing_url"
                read -p "Update remote origin to $REPO_URL? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    git remote set-url origin "$REPO_URL"
                    log_success "Remote origin updated"
                else
                    log_info "Keeping existing remote origin"
                fi
            else
                log_info "Remote origin already correctly configured"
            fi
        else
            git remote add origin "$REPO_URL"
            log_success "Remote origin added"
        fi
    fi
}

# Create initial commit
create_initial_commit() {
    if [[ "$INITIAL_COMMIT" == true ]]; then
        log_info "Creating initial commit..."
        
        # Check if there are already commits
        if git rev-parse HEAD >/dev/null 2>&1; then
            log_info "Repository already has commits"
            
            # Check if there are uncommitted changes
            if ! git diff-index --quiet HEAD; then
                log_info "Found uncommitted changes"
                git add .
                git commit -m "feat: initial development environment setup

🎮 Advanced Rubik's Cube Simulator - Development Environment

This commit establishes the complete development infrastructure:

✅ Development Environment:
- Python 3.11+ with virtual environment
- Comprehensive dependency management
- Cross-platform compatibility

🔧 Code Quality:
- Black formatting with 88-char line length  
- isort import sorting
- Flake8 linting with plugins
- MyPy strict type checking
- Bandit security scanning
- Pre-commit hooks automation

🧪 Testing Framework:
- Pytest with fixtures and parametrization
- Coverage reporting (HTML, XML, terminal)
- Property-based testing with Hypothesis
- Performance benchmarking
- Headless testing for CI/CD

🚀 CI/CD Pipeline:
- GitHub Actions workflows
- Multi-platform testing (Windows, macOS, Linux)
- Python 3.9-3.12 matrix testing
- Automated security scanning
- Release automation
- Performance monitoring

💻 Development Tools:
- VS Code workspace configuration
- Comprehensive debug configurations
- Task automation and shortcuts
- Docker development environment
- Docker Compose orchestration

📜 Automation Scripts:
- setup-dev.sh: One-command environment setup
- run-tests.sh: Comprehensive test runner
- build-release.sh: Automated release building
- Makefile: Development task shortcuts

🐳 Containerization:
- Production-optimized Docker images
- Development container with all tools
- Multi-service Docker Compose setup
- Volume management and networking

📋 Project Management:
- GitHub issue templates
- Pull request templates  
- Contributing guidelines
- Code of conduct

🎯 Ready for Implementation:
- Modular architecture designed
- API interfaces defined
- Performance requirements specified
- Security best practices implemented

The foundation is now complete for implementing the Advanced Rubik's Cube 
Simulator with authentic solving algorithms, realistic 3D graphics, and 
educational features for the speedcubing community.

🧩 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
                log_success "Committed development environment setup"
            else
                log_info "No uncommitted changes found"
            fi
        else
            # First commit
            git add .
            git commit -m "feat: initial project setup with comprehensive development environment

🎮 Advanced Rubik's Cube Simulator

Complete development environment setup for building a realistic 3D Rubik's Cube 
simulator with authentic solving algorithms and educational features.

🚀 Initial implementation includes:
- Development environment with Python 3.11+
- Code quality tools (Black, Flake8, MyPy, Bandit)
- Comprehensive testing framework (Pytest, Coverage, Benchmarks)
- GitHub Actions CI/CD pipeline
- VS Code development configuration
- Docker containerization
- Automation scripts and Makefile
- Project documentation and contributing guidelines

Ready for core implementation of cube mechanics, solving algorithms, 
and 3D graphics rendering.

🧩 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
            log_success "Initial commit created"
        fi
    fi
}

# Push to remote
push_to_remote() {
    if [[ "$PUSH_TO_REMOTE" == true ]]; then
        log_info "Pushing to remote repository..."
        
        # Check if remote is accessible
        if ! git ls-remote origin >/dev/null 2>&1; then
            log_error "Cannot access remote repository. Please check:"
            log_error "1. Repository URL is correct"
            log_error "2. You have access to the repository"
            log_error "3. Your authentication is set up (SSH keys or token)"
            exit 1
        fi
        
        # Push with appropriate flags
        push_args=("origin" "$BRANCH")
        if [[ "$FORCE_PUSH" == true ]]; then
            push_args=("--force" "${push_args[@]}")
            log_warning "Force pushing to remote"
        fi
        
        # Try to push
        if git push "${push_args[@]}" 2>/dev/null; then
            log_success "Successfully pushed to remote"
        else
            # If push fails, try with --set-upstream
            log_info "Setting upstream and pushing..."
            git push --set-upstream origin "$BRANCH"
            log_success "Successfully pushed with upstream set"
        fi
    fi
}

# Display next steps
show_next_steps() {
    echo ""
    echo "🎉 Repository synchronization complete!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Verify the repository on GitHub: ${REPO_URL%.git}"
    echo "  2. Set up branch protection rules (optional)"
    echo "  3. Configure GitHub Actions secrets if needed:"
    echo "     - CODECOV_TOKEN (for coverage reporting)"
    echo "     - PYPI_API_TOKEN (for package publishing)"
    echo "     - DOCKER_USERNAME & DOCKER_PASSWORD (for Docker Hub)"
    echo "  4. Invite collaborators to the repository"
    echo "  5. Start implementing the core cube engine!"
    echo ""
    echo "🔧 Development commands:"
    echo "  make setup-dev      # Set up development environment"
    echo "  make test          # Run test suite" 
    echo "  make run-headless  # Run application"
    echo "  make help          # Show all available commands"
    echo ""
    echo "🐳 Docker development:"
    echo "  docker-compose up rcsim-dev  # Start development container"
    echo ""
    echo "📚 Documentation:"
    echo "  - README.md: Project overview and setup"
    echo "  - CONTRIBUTING.md: Contribution guidelines"
    echo "  - docs/: Detailed documentation"
    echo ""
    echo "Happy coding! 🚀"
}

# Main function
main() {
    echo "🔄 Advanced Rubik's Cube Simulator - Repository Sync"
    echo "=================================================="
    echo ""
    
    validate_repo_url
    check_prerequisites
    setup_git_config
    setup_remote
    create_initial_commit
    push_to_remote
    show_next_steps
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        --no-setup-remote)
            SETUP_REMOTE=false
            shift
            ;;
        --no-initial-commit)
            INITIAL_COMMIT=false
            shift
            ;;
        --no-push)
            PUSH_TO_REMOTE=false
            shift
            ;;
        -f|--force-push)
            FORCE_PUSH=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
        *)
            if [[ -z "$REPO_URL" ]]; then
                REPO_URL="$1"
            else
                log_error "Multiple repository URLs provided"
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi