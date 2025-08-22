import os

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request

from services.orchestrator.core.orchestrator import Orchestrator
from services.orchestrator.integrations.github import verify_signature

from .schemas import FeatureIn, FeatureOut, FeatureStatusOut, TaskOut

app = FastAPI(title="Dark Software Factory - Orchestrator", version="0.1.0")

# Single orchestrator instance for MVP
orchestrator = Orchestrator()


@app.post("/features", response_model=FeatureOut)
async def create_feature(feature: FeatureIn, bg: BackgroundTasks):
    feat = orchestrator.submit_feature(title=feature.title, description=feature.description)
    # Kick off background execution
    bg.add_task(orchestrator.run_feature, feat.id)
    return FeatureOut.model_validate(feat.model_dump())


@app.get("/features/{feature_id}", response_model=FeatureStatusOut)
async def get_feature(feature_id: str):
    feat = orchestrator.get_feature(feature_id)
    if not feat:
        raise HTTPException(status_code=404, detail="Feature not found")
    return orchestrator.feature_status(feature_id)


@app.get("/features/{feature_id}/tasks", response_model=list[TaskOut])
async def list_feature_tasks(feature_id: str):
    feat = orchestrator.get_feature(feature_id)
    if not feat:
        raise HTTPException(status_code=404, detail="Feature not found")
    return [TaskOut.model_validate(t.model_dump()) for t in orchestrator.list_tasks(feature_id)]


@app.post("/github/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
    x_github_event: str | None = Header(default=None, alias="X-GitHub-Event"),
    bg: BackgroundTasks | None = None,
):
    secret = os.getenv("DSF_GITHUB_WEBHOOK_SECRET", "")
    payload = await request.body()
    if not secret or not verify_signature(secret, x_hub_signature_256 or "", payload):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Minimal ingestion: create a feature from newly opened GitHub issues
    try:
        event = x_github_event or ""
        body = await request.json()
    except Exception:
        event = x_github_event or ""
        body = {}

    if event == "issues" and body.get("action") == "opened":
        issue = body.get("issue", {})
        title = (issue.get("title") or "").strip()
        desc = issue.get("body") or ""
        if title:
            feat = orchestrator.submit_feature(title=title, description=desc)
            if bg is not None:
                bg.add_task(orchestrator.run_feature, feat.id)
            return {"ok": True, "event": event, "feature_id": feat.id}

    # Default acknowledgement
    return {"ok": True, "event": x_github_event}
