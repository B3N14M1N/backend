# FastAPI Threads/Groups Backend — Bootstrap

This repository is a FastAPI backend scaffold for a social threads/groups platform. This commit implements the repo bootstrap (T#001) and provides a minimal skeleton to continue development.

What's included:
- Project layout (`app/`, `app/api/`, `app/core/`, `app/data/`, `app/services/`)
- `requirements.txt` with core dependencies
- `.env.example` with env var placeholders
- `Dockerfile` and `docker-compose.yml` for local dev stack (Postgres, Redis, Mailhog)
- `scripts/rebuild.ps1` to build and run locally

Quick start (local - Docker):

1. Copy `.env.example` to `.env` and edit values.
2. Run the rebuild script:

	./scripts/rebuild.ps1

3. Open http://localhost:8000/docs for OpenAPI once the API starts.

Files created/edited in this task:
- `app/main.py` — minimal FastAPI app with `/healthz`
- `app/core/config.py` — basic Pydantic settings loader
- `requirements.txt`, `.env.example`, `Dockerfile`, `docker-compose.yml`
- `scripts/rebuild.ps1`, `.gitignore`

Local dev scripts (bash):
- `scripts/init_venv.sh` — create and populate a `.venv` from `requirements.txt`
- `scripts/run.sh` — activate `.venv` and start the app with uvicorn

PowerShell (Windows) helpers:
- `scripts/init_venv.ps1` — create and populate a `.venv` from `requirements.txt` (PowerShell)
- `scripts/run.ps1` — activate `.venv` and start the app with uvicorn (PowerShell)
- `docker/run.ps1` — stop, remove, rebuild, and run containers via Docker Compose
- `docker/cleanup.ps1` — clean up containers, optionally images, and free resources

PowerShell usage (from project root):

```powershell
# create venv and install deps
.\scripts\init_venv.ps1

# start the app
.\scripts\run.ps1

# rebuild containers
.\docker\run.ps1

# cleanup resources
.\docker\cleanup.ps1
```
Next steps:
- Implement settings & app factory, DB provider, models, repositories, and routers (T#002–T#006).

If you want, I can proceed to implement T#002 now and wire configuration into the app.
# backend