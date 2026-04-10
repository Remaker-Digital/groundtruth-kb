# Developer automation for groundtruth-kb
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

.PHONY: lint format format-check test test-cov check serve build clean install-dev docstring-cov

lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format --check .

test:
	pytest -v --tb=short

test-cov:
	pytest --cov=groundtruth_kb --cov-report=term-missing tests/

check: lint format-check test
	@echo "All checks passed."

serve:
	gt serve

build:
	python -m build --wheel

clean:
	rm -rf dist/ *.egg-info .ruff_cache __pycache__ site/ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

install-dev:
	pip install -e ".[dev,web]"

docstring-cov:
	interrogate src/groundtruth_kb/ --fail-under 50 -vv
