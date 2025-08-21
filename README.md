# Dark Software Factory (DSF) — MVP Scaffold

This repository contains the initial scaffold to develop the Dark Software Factory as described in the PRD.

PRD: dark-factory-prd.md

## Overview

MVP scope (Phase 1):
- Orchestrator API (FastAPI) for tasks and agent management
- Redis message bus (pub/sub) between orchestrator and agents
- Agent Runner that consumes tasks and produces events
- GitHub webhook endpoint stub for integration
- Basic conflict detection stub
- Simple test and CI setup
- Docker Compose for local dev with Redis and Postgres

Tech choices:
- API: FastAPI (Python 3.11)
- Message Bus: Redis Streams
- Storage: PostgreSQL (future; included in docker-compose)
- CI: GitHub Actions (lint + tests)
- Lint/Format: ruff + black
- Tests: pytest

## Repo Structure

- services/
  - orchestrator/ ... FastAPI app and orchestration core
  - agent_runner/ ... Worker that processes tasks and emits events
- docs/ ... Architecture notes and decision records
- .github/workflows ... CI workflows

## Quickstart

Prereqs:
- Docker + Docker Compose
- Python 3.11 (optional for running locally without docker)

Environment:
- Copy .env.example to .env and adjust values as needed

Local dev with Docker:
- docker compose up --build

Services:
- Orchestrator API: http://localhost:8000 (Swagger at /docs)
- Redis: redis://localhost:6379
- Postgres: postgres://postgres:postgres@localhost:5432/dsf (reserved for future persistence)

Make targets (local Python dev without Docker):
- make sync-deps    # install Python deps
- make api          # run orchestrator API
- make agent        # run agent runner
- make test         # run tests
- make lint         # run ruff + black check

## API Surface (MVP)

- GET /healthz
- POST /tasks     ... Accept high-level feature request; optionally manual_decomposition=true
- GET /agents     ... List available agent types
- POST /github/webhook ... GitHub webhook stub (signature validation TODO)

## Phase Alignment

- FR-1.x Task decomposition: Manual + simple stub included
- FR-2.x Agent management: Basic registry + spawn simulation in agent_runner
- FR-3.x GitHub integration: Webhook stub + placeholders
- FR-4.x Conflict resolution: Stub
- FR-5.x Inter-agent coms: Redis Streams
- FR-6.x Quality: CI, lint, tests minimal; future gates TBD
- FR-7.x Monitoring: To be added (dashboard)
- FR-8.x Human-in-loop: To be added
- FR-9.x Self-improvement: To be added

## Next Steps

- Implement persistence (SQLAlchemy + Alembic) for tasks, agents, and events
- Flesh out GitHub App integration (installation, PR lifecycle)
- Add dashboard service for activity visualization
- Expand agent fleet and negotiation/conflict resolution logic
- Add RBAC, secrets management, and security scanning