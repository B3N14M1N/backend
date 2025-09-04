from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routers.test_template import router as test_router
from app.core.database import get_db_provider


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    yield
    # Shutdown
    db_provider = get_db_provider()
    await db_provider.close()


app = FastAPI(
    title="FastAPI Template Backend",
    lifespan=lifespan
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


app.include_router(test_router)
