import pytest

from services.orchestrator.core.orchestrator import Orchestrator


@pytest.mark.asyncio
async def test_feature_flow():
    orch = Orchestrator()
    feat = orch.submit_feature("Hello", "Make it work")
    await orch.run_feature(feat.id)
    status = orch.feature_status(feat.id)
    assert status.completed == status.total
    assert status.failed == 0


@pytest.mark.asyncio
async def test_persistence_sqlite(tmp_path, monkeypatch):
    monkeypatch.setenv("DSF_DB", "sqlite")
    # Ensure db stores under tmp_path
    monkeypatch.chdir(tmp_path)
    orch = Orchestrator()
    feat = orch.submit_feature("Persisted", "Check DB")
    await orch.run_feature(feat.id)
    # Create a new orchestrator instance and fetch
    orch2 = Orchestrator()
    loaded = orch2.get_feature(feat.id)
    assert loaded is not None
    tasks = orch2.list_tasks(feat.id)
    assert tasks, "Should load tasks from DB"
