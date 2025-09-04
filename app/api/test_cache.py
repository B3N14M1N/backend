from fastapi import APIRouter, Depends, HTTPException
import os
from sqlmodel import SQLModel
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


def _fetch_roles_sync(db_url: str):
    # lightweight sync query using SQLModel/SQLAlchemy engine
    from sqlalchemy import create_engine

    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM roles ORDER BY id"))
        return [row[0] for row in result.fetchall()]


@router.get("/roles")
async def get_roles():
    """Return list of role names; cache result in redis for 30s."""
    r = redis_client()
    cache_key = "test:roles"
    cached = r.get(cache_key)
    if cached:
        return {"source": "redis", "roles": cached.split(",")}

    db_url = _build_db_url()
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as ex:
        roles = await loop.run_in_executor(ex, _fetch_roles_sync, db_url)

    if roles is None:
        raise HTTPException(status_code=500, detail="DB query failed")

    # store in redis
    try:
        r.set(cache_key, ",".join(roles), ex=30)
    except Exception:
        # ignore cache failures for the test
        pass

    return {"source": "db", "roles": roles}
