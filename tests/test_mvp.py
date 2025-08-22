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
