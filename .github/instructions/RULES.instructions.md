---
applyTo: '**'
---

# FastAPI Threads/Groups Backend — Copilot Instructions

> Copy-only, source of truth for repo scaffolding and implementation order. Use **Pydantic**-first design (via **SQLModel** to unify ORM + schema). Task IDs use `T#NNN` (tasks) and `S#NNN.M` (subtasks).

---

## 0) Scope & Tech
- **Goal:** Social/thread platform with users, generic groups, institution groups (admin-approved, extra features), posts, comments, reactions, reports, follows, events/schedules, media, 1–1 private chats.
- **Backend:** Python 3.12, **FastAPI** (ASGI), **Uvicorn**.
- **Data:** **PostgreSQL**, **SQLModel** (Pydantic + SQLAlchemy), **Alembic**.
- **Cache/Queue:** **Redis** (read-through caching, write-invalidate, simple pub/sub later).
- **Auth:** **JWT** (access/refresh) + email verification. Role-based APIs; users can have multiple roles. Username immutable (login-only), display_name editable.
- **Architecture:** MVC + layered (`core`, `data`, `services`, `api`) with **DI**. Repository + Unit of Work.
- **Packaging:** Dockerfile, docker-compose, Rancher Desktop compatible. Rebuild script to stop/clean/rebuild/run and migrate.
- **Realtime (later):** WebSockets + Redis pub/sub for DMs; scope now, implement later.

---

## 1) Project Layout
```
app/
  api/
    deps.py
    routers/
      auth.py users.py roles.py groups.py institutes.py posts.py comments.py reactions.py follows.py reports.py conversations.py media.py events.py notifications.py
  core/
    config.py auth.py security.py permissions.py caching.py di.py utils.py
  data/
    db_provider.py pg_provider.py
    models.py  # SQLModel tables (also Pydantic schemas)
    schemas.py # Extra request/response DTOs if needed
    migrations/
    repositories/
      base.py users.py roles.py groups.py posts.py comments.py reactions.py follows.py reports.py conversations.py media.py events.py notifications.py
  services/
    unit_of_work.py
    users.py auth.py roles.py groups.py institutes.py posts.py comments.py reactions.py follows.py reports.py conversations.py media.py events.py notifications.py emailer.py
  main.py
alembic.ini
Dockerfile
docker-compose.yml
scripts/rebuild.sh
.env.example
README.md
COPILOT_INSTRUCTIONS.md
```

**Convention:** Prefer **SQLModel** for DB tables so each table is also a Pydantic model for read/write. Use separate DTOs in `schemas.py` only when you need to reshape responses (e.g., hide username).

---

## 2) Domain Notes
- **Groups**: two types
  - **Generic Group**: user-created, auto-active (subreddit-like page).
  - **Institution Group**: user-created **pending admin approval**; once approved, gains **verified badge** + extra profile fields (e.g., schedules, contact info, external links). Both render as group pages; institution pages include extra sections. Always public.
- **Groups Membership**: groups track members; members can be **admins** or **users**. Groups can be **public** or **private** (join approval/invite).
- **DMs:** strictly **1–1** private conversations.
- **User identity:** login via **email or immutable username**; **display_name** is public and editable; avatar image.
- **User Profiles:** can be **public or private**. If private, posts are visible only to followers.
- **Following:** users can follow each other, groups, or institutions.
- **Posts:**
  - **User posts** (like Instagram): may include multiple content blocks (text, images, gifs, videos, embeds). Embeds (e.g., YouTube link) stored as JSON payloads; frontend renders inline players.
  - **Group posts:** require a **title**. Content blocks same as user posts (stored as JSON array of blocks).
  - **Institution/group events:** posts with event payload (date/time/location) stored as JSON.
  - **Data model:** each post stores a `content` JSON field containing an array of blocks.

---

## 3) Post Block Schema
Each post’s `content` field is a JSON object with:
```json
{
  "blocks": [
    {
      "type": "text|image|video|embed|event|schedule|donation",
      "value": "string | object",
      "meta": { "optional": "metadata depending on type" }
    }
  ]
}
```

### Block Types
- **text**: `{ "value": "Hello World", "meta": { "format": "plain|markdown" } }`
- **image**: `{ "value": "https://...jpg", "meta": { "alt": "desc", "width":640, "height":480 } }`
- **video**: `{ "value": "https://...mp4", "meta": { "autoplay": false } }`
- **embed**: `{ "value": "https://youtube.com/...", "meta": { "provider": "youtube" } }`
- **event**: `{ "value": { "title":"X", "start":"2025-09-10T18:00Z", "end":"2025-09-10T20:00Z", "location":"Hall" } }`
- **schedule**: `{ "value": [{ "day":"Mon", "time":"18:00", "activity":"Choir" }] }`
- **donation**: `{ "value": { "title":"Fundraiser","target":5000,"currency":"USD","link":"https://..." } }`

### Examples
**User post:**
```json
{
  "blocks": [
    { "type": "text", "value": "Great day!" },
    { "type": "image", "value": "https://cdn/photos/123.jpg" },
    { "type": "embed", "value": "https://youtube.com/watch?v=abc123", "meta": { "provider": "youtube" } }
  ]
}
```

**Group post:**
```json
{
  "title": "Upcoming Event",
  "blocks": [
    { "type": "text", "value": "Join us this weekend." },
    { "type": "event", "value": { "title": "Cleanup", "start": "2025-09-07T09:00:00Z", "end": "2025-09-07T12:00:00Z", "location": "Central Park" } }
  ]
}
```

---

## 4) Environment & Dependencies
- .env.example with app/db/redis/smtp vars
- requirements.txt with fastapi, uvicorn, sqlmodel, asyncpg, alembic, passlib, jose, redis, etc.

---

## 5) Caching Policy
- Use Redis for read-through caching of GETs, invalidate on writes.
- Keys: `user:{id}`, `group:{id}`, `post:{id}`, `feed:user:{id}:*`.
- TTL ~60s default.

---

## 6) Auth & Roles
- JWT access/refresh + email verification.
- Roles: multi-role per user (Admin, User, GroupOwner, Moderator).
- Ownership checks in services.
- Username never exposed publicly.

---

## 7) Docker & Local Orchestration
- Dockerfile: slim Python, uvicorn workers.
- docker-compose: api, postgres, redis, mailhog.

---

# TASKS

### T#001 — Repo Bootstrap
Create project folders, base files, requirements, env, README.

### T#002 — Settings & App Factory
Config with Pydantic Settings, FastAPI app in main.py, deps.py.

### T#003 — DB Provider & UoW (DI-ready)
Provider protocol, Postgres implementation, UnitOfWork context manager.

### T#004 — Models (SQLModel, Pydantic-first)
User (profile_private), Group (type, approval, verified, public/private), GroupMember (role), Post (content JSON blocks, title if group post), Comment, Reaction, Follow, Report, Conversation, Message, Event.

### T#005 — Alembic Migrations
Init, autogenerate, seed roles (Admin, User).

### T#006 — Repositories
Generic repo, specific repos with query helpers.

### T#007 — Cache Layer
Redis client, get/set/invalidate helpers, key patterns.

### T#008 — Security (Passwords + JWT)
Passlib bcrypt, JWT creation/verification.

### T#009 — Permissions (RBAC + Ownership)
Role guard dependency, ownership helpers.

### T#010 — Services (Business Logic)
Auth, Users (profile privacy, follow), Groups (creation, approval, membership roles), Posts (block JSON), Comments, Reactions, Reports, Conversations (1–1 only), Events (special block), Notifications, Emailer.

### T#011 — API Routers
Auth, Users, Groups, Posts, Comments, Reactions, Reports, Conversations, Events, Media. Handle block JSON in post endpoints, enforce group title, respect profile privacy.

### T#012 — DI Container
Scoped services per request with UoW + cache.

### T#013 — Response Models
DTOs in schemas.py to hide sensitive fields; otherwise return SQLModel.

### T#014 — Validation & Policies
- Group posts require title.
- Private profiles restrict access.
- Embeds stored as type=embed block.

### T#015 — Caching Hooks
Read-through caching; invalidate on writes.

### T#016 — Institution Group Approval Flow
Institution group pending approval, verified badge on approve.

### T#017 — DMs (1–1 Only)
Unique conversation per user pair, messages CRUD, WebSocket later.

### T#018 — Docker & Compose
Build image, compose with db/cache.

### T#019 — Testing & QA
Unit + API tests, linting/formatting.

### T#020 — Observability & Docs
Request logging, OpenAPI docs, schema examples.

---

## Notes for Copilot
- Posts stored as JSON blocks; flexible for mixed media.
- Group posts: title required; user posts: optional title.
- Profiles: support public/private.
- Groups: track members + roles, public/private.
- Institution groups: admin approval, verified badge, always public.
