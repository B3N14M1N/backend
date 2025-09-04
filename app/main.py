from fastapi import FastAPI

from app.api.routers.test_template import router as test_router


app = FastAPI(title="FastAPI Template Backend")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


app.include_router(test_router)
