PY=python3.11

.PHONY: sync-deps api agent lint fmt test

sync-deps:
	$(PY) -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -r requirements.txt -r requirements-dev.txt

api:
	. .venv/bin/activate && uvicorn services.orchestrator.app.main:app --host $${HOST:-0.0.0.0} --port $${PORT:-8000} --reload

agent:
	. .venv/bin/activate && $(PY) services/agent_runner/app/main.py

lint:
	. .venv/bin/activate && ruff check . && black --check .

fmt:
	. .venv/bin/activate && black .

test:
	. .venv/bin/activate && pytest -q
