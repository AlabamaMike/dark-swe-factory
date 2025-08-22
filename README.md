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

## Quality gate

- Lint & format check (ruff, black), tests with coverage, and Bandit security scan:

```bash
source .venv/bin/activate
ruff check . && black --check . && pytest && bandit -c pyproject.toml -r services
```

VS Code Task: “Quality Gate” (Run -> Tasks -> Quality Gate)

## GitHub integration (optional)

Set environment variables to enable branch/PR creation on task completion and to validate webhooks:

- `DSF_GITHUB_ENABLED=true`
- `DSF_GITHUB_TOKEN=<gh_token_with_repo_scope>`
- `DSF_GITHUB_REPO=owner/repo`
- `DSF_GITHUB_WEBHOOK_SECRET=<secret>`

Webhook endpoint: `POST /github/webhook` (expects `X-Hub-Signature-256`). For MVP, it just verifies and acknowledges the event.
