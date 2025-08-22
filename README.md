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

## Azure Key Vault (optional)

Set the following to load secrets from Key Vault using Managed Identity (in Azure) or Azure CLI login locally:

- `DSF_KEYVAULT_ENABLED=true`
- `DSF_KEYVAULT_URI=https://<your-vault-name>.vault.azure.net/`

Secrets read (with env fallback):

- `DSF_GITHUB_TOKEN`
- `DSF_GITHUB_REPO`
- `DSF_GITHUB_WEBHOOK_SECRET`
- `DSF_REDIS_URL`

Notes:
- In Azure, grant the app’s managed identity `Key Vault Secrets User` role on the vault.
- Locally, `az login` or set `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` for a service principal.

## Containers

Run the API and worker with Redis using Docker:

1. Optionally create a `.env` file with:
  - `DSF_GITHUB_ENABLED=true`
  - `DSF_GITHUB_TOKEN=ghp_xxx`
  - `DSF_GITHUB_REPO=owner/repo`
  - `DSF_GITHUB_WEBHOOK_SECRET=secret`

2. Start services:

```bash
docker compose up --build
```

API: http://localhost:8000

Note: SQLite DB lives inside the container by default. Mount a volume for persistence across runs.
