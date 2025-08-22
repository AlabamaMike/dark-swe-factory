VENV?=.venv

.PHONY: install fmt lint test cov bandit quality

install:
	python -m venv $(VENV)
	. $(VENV)/bin/activate; pip install -r requirements.txt

fmt:
	. $(VENV)/bin/activate; black .

lint:
	. $(VENV)/bin/activate; ruff check .

test:
	. $(VENV)/bin/activate; pytest

cov:
	. $(VENV)/bin/activate; pytest --cov=services --cov-report=term-missing

bandit:
	. $(VENV)/bin/activate; bandit -c pyproject.toml -r services

quality: lint test bandit
	@echo "Quality gate passed."
