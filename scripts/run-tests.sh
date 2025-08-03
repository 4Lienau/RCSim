#!/bin/bash
# Advanced Rubik's Cube Simulator - Test Runner Script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
COVERAGE=true
VERBOSE=false
PARALLEL=false
WATCH=false
HEADLESS=true
BENCHMARK=false

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Test runner for Advanced Rubik's Cube Simulator"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE       Test type: unit, integration, performance, all (default: all)"
    echo "  -c, --coverage        Generate coverage report (default: true)"
    echo "  -v, --verbose         Verbose output (default: false)"
    echo "  -p, --parallel        Run tests in parallel (default: false)"
    echo "  -w, --watch           Watch for file changes and re-run tests"
    echo "  -g, --gui             Run with GUI (not headless)"
    echo "  -b, --benchmark       Run performance benchmarks"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests with coverage"
    echo "  $0 -t unit -v         # Run unit tests with verbose output"
    echo "  $0 -t performance -b  # Run performance tests with benchmarks"
    echo "  $0 -w                 # Watch mode for development"
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

# Check if virtual environment is activated
check_venv() {
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
}

# Set up environment variables
setup_environment() {
    export PYTHONPATH="${PWD}/src:${PYTHONPATH:-}"
    export RCSIM_TESTING=1
    
    if [[ "$HEADLESS" == true ]]; then
        export SDL_VIDEODRIVER=dummy
        export DISPLAY=:99
    fi
    
    log_info "Environment configured for testing"
}

# Run unit tests
run_unit_tests() {
    log_info "Running unit tests..."
    
    local pytest_args=("tests/unit/")
    
    if [[ "$VERBOSE" == true ]]; then
        pytest_args+=("-v")
    fi
    
    if [[ "$COVERAGE" == true ]]; then
        pytest_args+=("--cov=src/rcsim" "--cov-report=term-missing" "--cov-report=html")
    fi
    
    if [[ "$PARALLEL" == true ]]; then
        pytest_args+=("-n" "auto")
    fi
    
    pytest "${pytest_args[@]}"
}

# Run integration tests
run_integration_tests() {
    log_info "Running integration tests..."
    
    local pytest_args=("tests/integration/")
    
    if [[ "$VERBOSE" == true ]]; then
        pytest_args+=("-v")
    fi
    
    if [[ "$COVERAGE" == true ]]; then
        pytest_args+=("--cov=src/rcsim" "--cov-append" "--cov-report=term-missing")
    fi
    
    # Integration tests typically shouldn't run in parallel
    pytest "${pytest_args[@]}"
}

# Run performance tests
run_performance_tests() {
    log_info "Running performance tests..."
    
    local pytest_args=("tests/performance/")
    
    if [[ "$VERBOSE" == true ]]; then
        pytest_args+=("-v")
    fi
    
    if [[ "$BENCHMARK" == true ]]; then
        pytest_args+=("--benchmark-only" "--benchmark-json=benchmark-results.json")
    else
        pytest_args+=("--benchmark-disable")
    fi
    
    pytest "${pytest_args[@]}"
}

# Run all tests
run_all_tests() {
    log_info "Running complete test suite..."
    
    local pytest_args=("tests/")
    
    if [[ "$VERBOSE" == true ]]; then
        pytest_args+=("-v")
    fi
    
    if [[ "$COVERAGE" == true ]]; then
        pytest_args+=("--cov=src/rcsim" "--cov-report=term-missing" "--cov-report=html" "--cov-report=xml")
    fi
    
    if [[ "$PARALLEL" == true ]]; then
        pytest_args+=("-n" "auto")
    fi
    
    # Exclude performance tests from regular runs unless specifically requested
    if [[ "$BENCHMARK" != true ]]; then
        pytest_args+=("--ignore=tests/performance/")
    fi
    
    pytest "${pytest_args[@]}"
}

# Watch mode for continuous testing
run_watch_mode() {
    log_info "Starting watch mode..."
    log_info "Watching for changes in src/ and tests/ directories..."
    log_info "Press Ctrl+C to stop"
    
    if ! command -v watchdog >/dev/null 2>&1; then
        log_info "Installing watchdog for file watching..."
        pip install watchdog
    fi
    
    python -c "
import time
import subprocess
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TestHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_run = 0
        self.debounce_time = 2  # seconds
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        if not event.src_path.endswith('.py'):
            return
        
        # Skip cache files
        if '__pycache__' in event.src_path:
            return
            
        current_time = time.time()
        if current_time - self.last_run < self.debounce_time:
            return
        
        self.last_run = current_time
        print(f'\\n🔄 File changed: {event.src_path}')
        
        # Run appropriate tests based on file location
        if 'tests/' in event.src_path:
            # If test file changed, run that specific test
            subprocess.run(['pytest', event.src_path, '-v', '--tb=short'])
        else:
            # If source file changed, run unit tests
            subprocess.run(['pytest', 'tests/unit/', '-v', '--tb=short', '-x'])

# Set up observers
observer = Observer()
observer.schedule(TestHandler(), 'src/', recursive=True)
observer.schedule(TestHandler(), 'tests/', recursive=True)

observer.start()
print('👀 Watching for changes... Press Ctrl+C to stop')

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    print('\\n👋 Watch mode stopped')

observer.join()
"
}

# Generate test report
generate_report() {
    if [[ "$COVERAGE" == true ]] && [[ -f ".coverage" ]]; then
        log_info "Generating test report..."
        
        coverage report --show-missing
        
        if [[ -d "htmlcov" ]]; then
            log_success "HTML coverage report generated in htmlcov/"
            
            # Try to open in browser on macOS/Linux
            if command -v open >/dev/null 2>&1; then
                open htmlcov/index.html
            elif command -v xdg-open >/dev/null 2>&1; then
                xdg-open htmlcov/index.html
            fi
        fi
    fi
    
    if [[ "$BENCHMARK" == true ]] && [[ -f "benchmark-results.json" ]]; then
        log_success "Benchmark results saved to benchmark-results.json"
    fi
}

# Main function
main() {
    echo "🧪 Advanced Rubik's Cube Simulator - Test Runner"
    echo "==============================================="
    echo ""
    
    check_venv
    setup_environment
    
    case "$TEST_TYPE" in
        "unit")
            run_unit_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "performance")
            run_performance_tests
            ;;
        "all")
            if [[ "$WATCH" == true ]]; then
                run_watch_mode
                return
            else
                run_all_tests
            fi
            ;;
        *)
            log_error "Unknown test type: $TEST_TYPE"
            usage
            exit 1
            ;;
    esac
    
    generate_report
    
    log_success "Testing completed!"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -w|--watch)
            WATCH=true
            shift
            ;;
        -g|--gui)
            HEADLESS=false
            shift
            ;;
        -b|--benchmark)
            BENCHMARK=true
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