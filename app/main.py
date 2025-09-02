from fastapi import FastAPI

app = FastAPI(title="Threads/Groups Backend")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
