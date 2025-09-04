from fastapi import APIRouter, HTTPException
import os
from sqlalchemy import text
from concurrent.futures import ThreadPoolExecutor
import asyncio

from app.core.caching import redis_client

router = APIRouter(prefix="/test", tags=["test"])


def _build_db_url() -> str:
    user = os.environ.get("POSTGRES_USER", "postgres")
    pw = os.environ.get("POSTGRES_PASSWORD", "change_me")
    db = os.environ.get("POSTGRES_DB", "appdb")
    host = os.environ.get("POSTGRES_HOST", "db")
    port = os.environ.get("POSTGRES_PORT", "5432")
    return f"postgresql://{user}:{pw}@{host}:{port}/{db}"


def _fetch_templates_sync(db_url: str):
    from sqlalchemy import create_engine

    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, title, status, created_at FROM templateitem ORDER BY id"))
        return [ {"id": row[0], "title": row[1], "status": row[2], "created_at": str(row[3])} for row in result.fetchall() ]


@router.get("/template")
async def get_templates():
    """Return list of template items; cache result in redis for 30s."""
    r = redis_client()
    cache_key = "test:template"
    try:
        cached = r.get(cache_key)
    except Exception:
        cached = None
    if cached:
        items = []
        for s in cached.split("||"):
            if not s:
                continue
            parts = s.split("::", 3)
            items.append({"id": int(parts[0]), "title": parts[1], "status": parts[2], "created_at": parts[3]})
        return {"source": "redis", "templates": items}

    db_url = _build_db_url()
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as ex:
        items = await loop.run_in_executor(ex, _fetch_templates_sync, db_url)

    if items is None:
        raise HTTPException(status_code=500, detail="DB query failed")

    # store in redis with simple serialization
    try:
        serialized = "||".join([f"{i['id']}::{i['title']}::{i['status']}::{i['created_at']}" for i in items])
        r.set(cache_key, serialized, ex=30)
    except Exception:
        pass

    return {"source": "db", "templates": items}
