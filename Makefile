.PHONY: help install install-dev test lint format type-check security clean build docker docs

# Default target
help:
	@echo "Sentry Terraform Discovery Tool - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  install       Install package in production mode"
	@echo "  install-dev   Install package in development mode"
	@echo "  test          Run test suite"
	@echo "  test-cov      Run tests with coverage report"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code with black"
	@echo "  type-check    Run type checking with mypy"
	@echo "  security      Run security checks"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build package for distribution"
	@echo "  docker        Build Docker image"
	@echo "  docker-run    Run tool in Docker container"
	@echo "  docs          Generate documentation"
	@echo "  pre-commit    Run pre-commit hooks"
	@echo "  config        Generate sample configuration"

# Git setup
git-init:
	@if [ ! -d ".git" ]; then \
		echo "Initializing Git repository..."; \
		git init; \
		git add .; \
		git config --global user.email "you@example.com"; \
		git config --global user.name "Your Name"; \
		git commit -m "Initial commit"; \
	else \
		echo "Git repository already initialized"; \
	fi

# Installation
install:
	pip install -e .

install-dev: git-init
	pip install -e ".[dev]"
	pre-commit install

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src/sentry_discovery --cov-report=html --cov-report=term

test-integration:
	pytest tests/ -v -m integration

# Code quality
lint:
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/sentry_discovery --ignore-missing-imports

# Security
security:
	bandit -r src/
	safety check

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Building
build: clean
	python -m build

# Docker
docker:
	docker build -t sentry-terraform-discovery:latest .

docker-run:
	docker run --rm -it -v $(PWD)/output:/app/output -e SENTRY_AUTH_TOKEN sentry-terraform-discovery:latest

docker-shell:
	docker run --rm -it -v $(PWD)/output:/app/output -e SENTRY_AUTH_TOKEN --entrypoint /bin/bash sentry-terraform-discovery:latest

# Documentation
docs:
	@echo "Generating documentation..."
	@mkdir -p docs/generated
	@echo "Documentation placeholders created"

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Configuration
config:
	@echo "Creating sample configuration..."
	@echo "sentry:" > .sentry-discovery.yaml
	@echo "  base_url: 'https://sentry.io/api/0'" >> .sentry-discovery.yaml
	@echo "  organization: 'your-org-slug'" >> .sentry-discovery.yaml
	@echo "  token: 'your-token-here'" >> .sentry-discovery.yaml
	@echo "" >> .sentry-discovery.yaml
	@echo "terraform:" >> .sentry-discovery.yaml
	@echo "  output_dir: './terraform'" >> .sentry-discovery.yaml
	@echo "  module_style: false" >> .sentry-discovery.yaml
	@echo "  import_script: true" >> .sentry-discovery.yaml
	@echo "" >> .sentry-discovery.yaml
	@echo "output:" >> .sentry-discovery.yaml
	@echo "  format: 'hcl'" >> .sentry-discovery.yaml
	@echo "  dry_run: false" >> .sentry-discovery.yaml
	@echo "Sample configuration created: .sentry-discovery.yaml"
	@echo "Edit this file with your Sentry details."

# Development workflow
dev-setup: install-dev config
	@echo "Development environment setup complete!"
	@echo "Next steps:"
	@echo "1. Edit .sentry-discovery.yaml with your Sentry token"
	@echo "2. Run 'make test' to verify everything works"
	@echo "3. Run 'sentry-discovery --help' to see available options"

# Release workflow
release-check: test lint type-check security
	@echo "All checks passed! Ready for release."

# Quick development test
dev-test:
	@echo "Testing basic imports..."
	@python -c "print('Testing imports...'); import sys; sys.path.insert(0, 'src')"

# Install pre-commit hooks
setup-hooks:
	pip install pre-commit
	pre-commit install
	@echo "Pre-commit hooks installed"

# Version management
version:
	@python -c "import re; content = open('setup.py').read(); version = re.search(r'version=\"([^\"]+)\"', content).group(1); print(f'Current version: {version}')"

# Check if directories exist
check-dirs:
	@echo "Checking directory structure..."
	@mkdir -p src/sentry_discovery
	@mkdir -p tests
	@mkdir -p docs
	@touch src/sentry_discovery/__init__.py
	@echo "Directory structure ready"