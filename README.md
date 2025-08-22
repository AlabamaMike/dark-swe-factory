# Dark Software Factory (DSF)

MVP scaffold for an asynchronous SWE agent swarm orchestrator per the PRD. Includes a minimal orchestrator, 3 agent stubs (code, test, review), a simple DAG builder, and a FastAPI service.

## Quick start

- Python 3.11+
- Install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Run the API:

```bash
uvicorn services.orchestrator.app.main:app --reload
```

- Submit a feature request:

```bash
curl -sS -X POST http://localhost:8000/features \
  -H 'Content-Type: application/json' \
  -d '{"title":"Add user authentication with OAuth2","description":"Implement OAuth2 login and protected routes"}' | jq
```

## Repo layout

- `services/orchestrator/core`: orchestrator, DAG, agents, models
- `services/orchestrator/app`: FastAPI app and routers
- `tests`: minimal tests
- `docs/implementation-plan.md`: plan to build the factory with the factory

## Status

MVP-only. Non-persistent in-memory state. Not production-ready.
