from fastapi import FastAPI

from app.api.test_cache import router as test_router


app = FastAPI(title="Threads/Groups Backend")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


app.include_router(test_router)
