# FastAPI Threads/Groups Backend — Bootstrap

Minimal bootstrap for a FastAPI-based social threads/groups backend. This repository contains a small FastAPI app, Docker development stack (Postgres, Redis, MailHog), and helper scripts tuned for Windows/PowerShell local development.

## Quick summary
- Framework: FastAPI (app skeleton in `app/`).
- Python: Tested with Python 3.11 (recommended).
- DB: PostgreSQL (containerized).
- Cache: Redis (containerized).
- Local SMTP: MailHog (containerized).
- Docker Compose is used to run the full local stack.

## Project structure (high level)
```
app/
  api/                # API routers will go here
  core/               # config, security, utils
  data/               # db provider, models, repositories
  services/           # business logic / unit of work
  main.py             # app entrypoint (uvicorn)

docker/               # PowerShell scripts for docker workflows
scripts/              # local dev PowerShell helpers (venv, run)

Dockerfile
docker-compose.yml
requirements.txt
.env.example
README.md
COPILOT.md
COPILOT_INSTRUCTIONS.md
```

Files of interest (current):
- `app/main.py` — minimal FastAPI app and health endpoint.
- `app/core/config.py` — Pydantic `Settings` for environment config.
- `requirements.txt` — pinned dependencies; adjusted for compatibility with FastAPI.
- `Dockerfile` — builds the API image (uses Python 3.11 base image).
- `docker-compose.yml` — development stack: `api`, `db`, `redis`, `mailhog`.
- `docker/run.ps1` — PowerShell script to build/run the compose stack.
- `docker/cleanup.ps1` — interactive cleanup (stop containers, optionally remove images/prune).
- `scripts/init_venv.ps1` — create & populate a Python virtualenv on Windows.
- `scripts/run.ps1` — run the app locally with the venv (uvicorn).

## Docker and named volumes
The compose file defines named volumes so they appear with readable names on the host. Current named volumes:
- `backend_db_data` — Postgres data
- `backend_redis_data` — Redis data
- `backend_mailhog_data` — MailHog data

If you changed `docker-compose.yml` manually, recreate the stack so the named volumes are created/used:

```powershell
# Stop and remove the current stack (keeps named volumes unless -v used)
docker compose down --remove-orphans

# Start stack and force rebuild of the API image
docker compose up -d --build
```

If you want to remove anonymous volumes and switch entirely to the named ones (destructive):

```powershell
# This removes volumes attached to the stack (data loss if volumes contain app data)
docker compose down -v --remove-orphans

# Then recreate
docker compose up -d --build
```

Use these commands only if you are sure you don't need existing container data.

## Quickstart (Windows / PowerShell)
1. Copy `.env.example` to `.env` and update values (at minimum: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `SECRET_KEY`).
2. Initialize a venv and install dependencies (optional if using containers):

```powershell
# from repo root
.\scripts\init_venv.ps1
```

3. To run the full Docker stack (recommended for a consistent dev environment):

```powershell
.\docker\run.ps1
```

4. To run the API locally using the venv (no docker):

```powershell
.\scripts\run.ps1
```
