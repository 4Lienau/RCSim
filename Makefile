# Advanced Rubik's Cube Simulator - Makefile
# Provides convenient shortcuts for common development tasks

.PHONY: help install install-dev test test-unit test-integration test-performance
.PHONY: lint format type-check security-check quality pre-commit
.PHONY: run run-headless debug profile benchmark
.PHONY: docs docs-serve docs-clean build clean release docker
.PHONY: setup-dev setup-hooks setup-vscode

# Default target
.DEFAULT_GOAL := help

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Variables
PYTHON := python3
PIP := pip
VENV_DIR := venv
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs

help: ## Show this help message
	@echo "$(CYAN)Advanced Rubik's Cube Simulator - Development Commands$(RESET)"
	@echo "======================================================"
	@echo ""
	@echo "$(GREEN)Setup Commands:$(RESET)"
	@grep -E '^setup-[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Development Commands:$(RESET)"
	@grep -E '^(install|run|debug|profile|benchmark)[a-zA-Z_-]*:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Code Quality Commands:$(RESET)"
	@grep -E '^(test|lint|format|type-check|security-check|quality|pre-commit)[a-zA-Z_-]*:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Documentation Commands:$(RESET)"
	@grep -E '^docs[a-zA-Z_-]*:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Build Commands:$(RESET)"
	@grep -E '^(build|clean|release|docker)[a-zA-Z_-]*:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'

# Setup Commands
setup-dev: ## Set up development environment
	@echo "$(GREEN)Setting up development environment...$(RESET)"
	@chmod +x scripts/setup-dev.sh
	@./scripts/setup-dev.sh

setup-hooks: ## Install pre-commit hooks
	@echo "$(GREEN)Installing pre-commit hooks...$(RESET)"
	@pre-commit install

setup-vscode: ## Set up VS Code workspace
	@echo "$(GREEN)Setting up VS Code workspace...$(RESET)"
	@code rcsim.code-workspace

# Installation Commands
install: ## Install package in current environment
	@echo "$(GREEN)Installing package...$(RESET)"
	@$(PIP) install -e .

install-dev: ## Install development dependencies
	@echo "$(GREEN)Installing development dependencies...$(RESET)"
	@$(PIP) install -r requirements-dev.txt
	@$(PIP) install -e .

# Testing Commands
test: ## Run all tests with coverage
	@echo "$(GREEN)Running all tests...$(RESET)"
	@chmod +x scripts/run-tests.sh
	@./scripts/run-tests.sh

test-unit: ## Run unit tests only
	@echo "$(GREEN)Running unit tests...$(RESET)"
	@pytest $(TEST_DIR)/unit/ -v

test-integration: ## Run integration tests only
	@echo "$(GREEN)Running integration tests...$(RESET)"
	@pytest $(TEST_DIR)/integration/ -v

test-performance: ## Run performance tests with benchmarks
	@echo "$(GREEN)Running performance tests...$(RESET)"
	@pytest $(TEST_DIR)/performance/ -v --benchmark-only

test-watch: ## Run tests in watch mode
	@echo "$(GREEN)Starting test watch mode...$(RESET)"
	@./scripts/run-tests.sh --watch

test-coverage: ## Generate coverage report
	@echo "$(GREEN)Generating coverage report...$(RESET)"
	@pytest $(TEST_DIR)/ --cov=$(SRC_DIR)/rcsim --cov-report=html --cov-report=term-missing
	@echo "$(YELLOW)Coverage report generated in htmlcov/$(RESET)"

# Code Quality Commands
lint: ## Run linting with flake8
	@echo "$(GREEN)Running linting...$(RESET)"
	@flake8 $(SRC_DIR)/ $(TEST_DIR)/

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(RESET)"
	@black $(SRC_DIR)/ $(TEST_DIR)/
	@isort $(SRC_DIR)/ $(TEST_DIR)/

type-check: ## Run type checking with mypy
	@echo "$(GREEN)Running type checking...$(RESET)"
	@mypy $(SRC_DIR)/

security-check: ## Run security checks with bandit
	@echo "$(GREEN)Running security checks...$(RESET)"
	@bandit -r $(SRC_DIR)/

quality: format lint type-check security-check ## Run all code quality checks
	@echo "$(GREEN)All code quality checks completed!$(RESET)"

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(GREEN)Running pre-commit hooks...$(RESET)"
	@pre-commit run --all-files

# Development Commands
run: ## Run the application
	@echo "$(GREEN)Starting application...$(RESET)"
	@$(PYTHON) $(SRC_DIR)/rcsim/main.py

run-headless: ## Run application in headless mode
	@echo "$(GREEN)Starting application (headless)...$(RESET)"
	@SDL_VIDEODRIVER=dummy $(PYTHON) $(SRC_DIR)/rcsim/main.py --headless

debug: ## Run application with debugger
	@echo "$(GREEN)Starting application with debugger...$(RESET)"
	@$(PYTHON) -m pdb $(SRC_DIR)/rcsim/main.py

profile: ## Profile application performance
	@echo "$(GREEN)Profiling application...$(RESET)"
	@$(PYTHON) -m cProfile -o profile.prof $(SRC_DIR)/rcsim/main.py --headless --benchmark
	@echo "$(YELLOW)Profile saved to profile.prof$(RESET)"

benchmark: ## Run performance benchmarks
	@echo "$(GREEN)Running benchmarks...$(RESET)"
	@pytest $(TEST_DIR)/performance/ --benchmark-only --benchmark-json=benchmark.json
	@echo "$(YELLOW)Benchmark results saved to benchmark.json$(RESET)"

# Documentation Commands
docs: ## Build documentation
	@echo "$(GREEN)Building documentation...$(RESET)"
	@cd $(DOCS_DIR) && make html
	@echo "$(YELLOW)Documentation built in $(DOCS_DIR)/_build/html/$(RESET)"

docs-serve: ## Serve documentation locally
	@echo "$(GREEN)Serving documentation on http://localhost:8000$(RESET)"
	@cd $(DOCS_DIR)/_build/html && $(PYTHON) -m http.server 8000

docs-clean: ## Clean documentation build
	@echo "$(GREEN)Cleaning documentation build...$(RESET)"
	@cd $(DOCS_DIR) && make clean

docs-watch: ## Build docs and watch for changes
	@echo "$(GREEN)Building docs with auto-reload...$(RESET)"
	@cd $(DOCS_DIR) && sphinx-autobuild . _build/html --host 0.0.0.0 --port 8000

# Build Commands
build: ## Build Python package
	@echo "$(GREEN)Building package...$(RESET)"
	@$(PYTHON) -m build
	@echo "$(YELLOW)Package built in dist/$(RESET)"

clean: ## Clean build artifacts and cache
	@echo "$(GREEN)Cleaning build artifacts...$(RESET)"
	@rm -rf build/
	@rm -rf dist/
	@rm -rf $(SRC_DIR)/*.egg-info/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	@rm -rf *.prof benchmark.json

clean-all: clean docs-clean ## Clean everything including docs
	@echo "$(GREEN)Deep clean completed!$(RESET)"

release: ## Build release (requires version: make release VERSION=1.0.0)
	@echo "$(GREEN)Building release...$(RESET)"
	@chmod +x scripts/build-release.sh
	@./scripts/build-release.sh --version $(VERSION)

release-dry: ## Dry run release build
	@echo "$(GREEN)Dry run release build...$(RESET)"
	@chmod +x scripts/build-release.sh
	@./scripts/build-release.sh --version $(VERSION) --dry-run

# Docker Commands
docker: ## Build Docker images
	@echo "$(GREEN)Building Docker images...$(RESET)"
	@docker build -t rcsim:latest .
	@docker build -f Dockerfile.dev -t rcsim:dev .

docker-dev: ## Run development environment in Docker
	@echo "$(GREEN)Starting development container...$(RESET)"
	@docker-compose up rcsim-dev

docker-test: ## Run tests in Docker
	@echo "$(GREEN)Running tests in Docker...$(RESET)"
	@docker-compose --profile testing up rcsim-test

docker-docs: ## Serve documentation in Docker
	@echo "$(GREEN)Serving documentation in Docker...$(RESET)"
	@docker-compose --profile docs up rcsim-docs

docker-clean: ## Clean Docker images and containers
	@echo "$(GREEN)Cleaning Docker artifacts...$(RESET)"
	@docker-compose down -v --rmi all --remove-orphans 2>/dev/null || true
	@docker system prune -f

# Utility Commands
install-tools: ## Install additional development tools
	@echo "$(GREEN)Installing additional tools...$(RESET)"
	@$(PIP) install \
		jupyter \
		ipython \
		py-spy \
		memory-profiler \
		line-profiler \
		vulture \
		radon

env-info: ## Show environment information
	@echo "$(CYAN)Environment Information$(RESET)"
	@echo "======================="
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Python path: $$(which $(PYTHON))"
	@echo "Pip version: $$($(PIP) --version)"
	@echo "Virtual env: $${VIRTUAL_ENV:-Not activated}"
	@echo "Working dir: $$(pwd)"
	@echo "Git branch: $$(git branch --show-current 2>/dev/null || echo 'Not a git repo')"
	@echo "Git status: $$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ') files changed"

quick-check: format lint test-unit ## Quick development check (format, lint, unit tests)
	@echo "$(GREEN)Quick check completed! ✅$(RESET)"

full-check: quality test docs ## Full check (all quality checks, tests, docs)
	@echo "$(GREEN)Full check completed! 🎉$(RESET)"

# CI/CD simulation
ci: ## Simulate CI pipeline
	@echo "$(GREEN)Simulating CI pipeline...$(RESET)"
	@make clean
	@make install-dev
	@make quality
	@make test
	@make build
	@make docs
	@echo "$(GREEN)CI pipeline completed! 🚀$(RESET)"

# Development workflow shortcuts
dev: install-dev setup-hooks ## Set up development environment quickly
	@echo "$(GREEN)Development environment ready! 🛠️$(RESET)"

check: format lint type-check ## Quick code quality check
	@echo "$(GREEN)Code quality check completed! ✨$(RESET)"

# Help for specific make targets
help-setup: ## Show setup help
	@echo "$(CYAN)Setup Commands Help$(RESET)"
	@echo "==================="
	@echo ""
	@echo "$(GREEN)make setup-dev$(RESET)    - Complete development environment setup"
	@echo "$(GREEN)make dev$(RESET)          - Quick development setup (install + hooks)"
	@echo "$(GREEN)make setup-hooks$(RESET)  - Install pre-commit hooks only"
	@echo "$(GREEN)make setup-vscode$(RESET) - Open VS Code workspace"

help-test: ## Show testing help
	@echo "$(CYAN)Testing Commands Help$(RESET)"
	@echo "====================="
	@echo ""
	@echo "$(GREEN)make test$(RESET)             - Run all tests with coverage"
	@echo "$(GREEN)make test-unit$(RESET)        - Run unit tests only"
	@echo "$(GREEN)make test-integration$(RESET) - Run integration tests only"
	@echo "$(GREEN)make test-performance$(RESET) - Run performance tests"
	@echo "$(GREEN)make test-watch$(RESET)       - Run tests in watch mode"
	@echo "$(GREEN)make test-coverage$(RESET)    - Generate detailed coverage report"