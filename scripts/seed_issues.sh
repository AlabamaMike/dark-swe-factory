#!/usr/bin/env bash
set -euo pipefail

repo="${1:-AlabamaMike/dark-swe-factory}"

features=(
  "Add GitHub integration|Create branches/PRs per task, webhook receiver, backoff"
  "Add SQLite persistence|Persist features, tasks, and runs; migration setup"
  "Add linting and coverage gates|Enforce ruff/black/coverage; review agent gating"
  "Add Redis queue|Priority queue and workers per agent type"
  "Add conflict resolution agent|Three-way merge helper and escalation"
  "Add WebSocket dashboard|Real-time task and agent activity"
)

for f in "${features[@]}"; do
  IFS='|' read -r title body <<<"$f"
  gh issue create --repo "$repo" --title "[Feature] $title" --label feature --body "$body" || true
done

echo "Seeded feature issues to $repo"