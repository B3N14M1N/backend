# FastAPI Threads/Groups Backend — Bootstrap

Minimal bootstrap for a FastAPI-based social threads/groups backend. This repository contains a small FastAPI app, Docker development stack (Postgres, Redis, MailHog), and helper scripts tuned for Windows/PowerShell local development.

## Quick summary
- Framework: FastAPI (app skeleton in `app/`).
- Python: Tested with Python 3.11 (recommended).
- DB: PostgreSQL (containerized).
- Cache: Redis (containerized).
- Local SMTP: MailHog (containerized).
- Docker Compose is used to run the full local stack.

Backend — Minimal Template

This repository is a reusable template for a FastAPI backend using SQLModel (Pydantic + SQLAlchemy), Alembic migrations, Postgres and Redis. It includes helper scripts for local development and a minimal example model + seeder to exercise DB + Redis caching.

Quick overview
- Framework: FastAPI
- Models: SQLModel (Pydantic + SQLAlchemy)
- DB: PostgreSQL (docker-compose)
- Cache: Redis
- Migrations: Alembic

Requirements
- Docker & Docker Compose
- PowerShell (Windows) or a POSIX shell for scripts

Setup (local dev)
1. Copy `.env.example` to `.env` and update credentials.
2. Start services (build + recreate containers):

```powershell
.\scripts\setup\run.ps1
```

3. Create the initial migration and apply it:

```powershell
.\scripts\db\db.ps1 -Init
# Use -f to auto-remove any existing files under alembic\versions
```

Seeding & testing
- Seed a small template row:

```powershell
.\scripts\db\seed-template.ps1
```

- Test the demo cache endpoint (after API is running):

```powershell
curl.exe http://127.0.0.1:8000/test/template
```

Or go to the api [docs](http://localhost:8000/docs)

How to extend
- Add models to `app/data/schemas/models.py`.
- Create revisions with `./scripts/db/db.ps1 -Revision -Message "desc"` and apply with `-Upgrade`.
- Add routers in `app/api/routers/` and include them in `app/main.py`.

