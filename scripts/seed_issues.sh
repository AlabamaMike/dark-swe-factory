#!/usr/bin/env bash
set -euo pipefail

repo="${1:-AlabamaMike/dark-swe-factory}"

# Ensure labels exist
gh label create feature --repo "$repo" --color 1f883d --description "High-level DSF feature" 2>/dev/null || true
gh label create task --repo "$repo" --color fbca04 --description "Agent-executable task" 2>/dev/null || true

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
  full_title="[Feature] $title"
  # Check if an open issue with this title exists
  count=$(gh issue list --repo "$repo" --search "in:title \"$full_title\" state:open" --limit 1 --json number --jq 'length')
  if [ "$count" -gt 0 ]; then
    num=$(gh issue list --repo "$repo" --search "in:title \"$full_title\" state:open" --limit 1 --json number --jq '.[0].number')
    gh issue edit "$num" --repo "$repo" --add-label feature >/dev/null 2>&1 || true
    echo "Skipped (exists): $full_title (#$num)"
  else
    gh issue create --repo "$repo" --title "$full_title" --label feature --body "$body" >/dev/null 2>&1 || true
    echo "Created: $full_title"
  fi
done

echo "Seeded feature issues to $repo"