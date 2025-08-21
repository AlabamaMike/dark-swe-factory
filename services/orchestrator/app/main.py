from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
import redis.asyncio as redis

from .config import settings
from .routers import health, tasks, agents, github

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting orchestrator...")
    app.state.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield
    finally:
        logger.info("Shutting down orchestrator...")
        await app.state.redis.close()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(agents.router)
app.include_router(github.router)
