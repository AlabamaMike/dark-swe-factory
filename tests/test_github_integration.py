import pytest

from services.orchestrator.core.orchestrator import Orchestrator
from services.orchestrator.integrations.github import verify_signature


def test_verify_signature():
    secret = "s3cr3t"
    payload = b"{}"
    import hashlib
    import hmac

    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_signature(secret, f"sha256={sig}", payload)
    assert not verify_signature(secret, "sha256=deadbeef", payload)


@pytest.mark.asyncio
async def test_orchestrator_github_hook(monkeypatch):
    # Enable integration with dummy creds
    monkeypatch.setenv("DSF_GITHUB_ENABLED", "true")
    monkeypatch.setenv("DSF_GITHUB_TOKEN", "fake")
    monkeypatch.setenv("DSF_GITHUB_REPO", "owner/repo")

    calls = []

    class DummyClient:
        def __init__(self, *a, **k):
            pass

        def create_branch(self, branch, from_sha=None):
            calls.append(("branch", branch))

        def create_or_update_file(self, path, content, message, branch):
            calls.append(("file", path, branch))

        def create_pull_request(self, branch, title, body=""):
            calls.append(("pr", branch))
            return 1

    monkeypatch.setattr(
        "services.orchestrator.core.orchestrator.GitHubClient", DummyClient, raising=True
    )

    orch = Orchestrator()
    feat = orch.submit_feature("GH Hook", "demo")
    await orch.run_feature(feat.id)
    # We expect at least one call (the last task completion creates a PR)
    assert any(c[0] == "pr" for c in calls)
    # Running again should not create duplicate PRs due to persistence guard
    prev_count = len([c for c in calls if c[0] == "pr"])
    await orch.run_feature(feat.id)
    assert len([c for c in calls if c[0] == "pr"]) == prev_count
