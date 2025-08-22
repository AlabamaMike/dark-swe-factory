from fastapi import FastAPI, BackgroundTasks, HTTPException
from .schemas import FeatureIn, FeatureOut, FeatureStatusOut, TaskOut
from services.orchestrator.core.orchestrator import Orchestrator

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
