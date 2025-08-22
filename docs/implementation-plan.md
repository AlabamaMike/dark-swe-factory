# DSF Implementation Plan (Build the Factory with the Factory)

This plan turns the PRD into increments. We bootstrap a minimal orchestrator and let agents expand it iteratively.

## Objectives
- Deliver PRD Phase 1 MVP with 3 agent types, single repo, simple dashboard/API
- Enable self-hosted iteration: the factory generates tasks to enhance itself

## Milestones

1) Bootstrap (Day 1-2)
- Minimal orchestrator + DAG runner
- Agent stubs (code, test, review)
- FastAPI endpoints: submit feature, status, list tasks
- Basic tests and CI skeleton

2) GitHub Loop (Day 3-5)
- Add GitHub App integration (webhook receiver, PR creation)
- Branch per task, PR on completion
- Persist state (SQLite initially)

3) Quality Gates (Week 2)
- Run pytest + coverage
- Linting (ruff/black) and simple SAST (bandit)
- Review agent enforces thresholds before PR

4) Decomposition v1 (Week 2)
- Replace basic DAG with heuristic decomposition (detect API/db/docs tasks)
- Add acceptance criteria generation

5) Queue & Concurrency (Week 3)
- Redis-based priority queue
- Worker pods or processes per agent type

6) Dashboard (Week 3)
- Minimal web UI to visualize features, tasks, and agent activity via websockets

7) Conflict Handling v1 (Week 4)
- Detect merge conflicts, spawn conflict agent
- Three-way merge helper and escalation

## Build-the-factory loop

- Seed features (this repo):
  - "Add GitHub integration"
  - "Add SQLite persistence"
  - "Add linting and coverage gates"
  - "Add Redis queue"
  - "Add conflict agent"
- For each feature: orchestrator decomposes -> code agent implements -> test agent writes tests -> review agent gates
- Merge via PRs; track velocity and coverage

## Contracts
- Task: { id, title, description, agent_type, depends_on[], status, result }
- Feature: { id, title, description, task_ids[] }

## Risks & Mitigations
- API keys & secrets: use dotenv now, migrate to Vault
- Rate limits: backoff + caching; batch queries
- Flaky tests: retry policy + isolation

## Next Up (Actionable)
- Add `pyproject.toml` with tool configs
- Add GitHub App skeleton (routes, signature verify)
- Introduce persistence layer interface + SQLite impl
- CLI to submit features and tail status
