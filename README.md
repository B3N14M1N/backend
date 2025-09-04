# FastAPI Backend Template

FastAPI template with async PostgreSQL, Redis caching, dependency injection, and clean architecture.

## Project Structure

```
app/
├── api/routers/           # API endpoints
├── core/                  # Infrastructure (database, dependencies, config)
├── data/
│   ├── repositories/      # Data access layer
│   └── schemas/           # Database models
└── services/              # Business logic
```

## Quick Start

```powershell
.\scripts\setup\run.ps1
.\scripts\setup\db.ps1 -Init
.\scripts\db\seed-template.ps1
```

Access API at http://localhost:8000/docs

## How to Extend

### Add Database Model
1. Define model in `app/data/schemas/models.py`
2. Create migration: `.\scripts\setup\db.ps1 -Revision -Message "add model"`
3. Apply migration: `.\scripts\setup\db.ps1 -Upgrade`

### Add Repository
Create `app/data/repositories/my_repository.py`:
```python
class MyRepository:
    def __init__(self, db_provider: DatabaseProvider):
        self.db_provider = db_provider
    
    async def get_all(self) -> List[dict]:
        async with self.db_provider.get_session() as session:
            # Database operations
```

### Add Service
Create `app/services/my_service.py`:
```python
class MyService:
    def __init__(self, repository: MyRepository):
        self.repository = repository
    
    async def get_items(self) -> dict:
        return await self.repository.get_all()
```

### Add Dependency
Add to `app/core/dependencies.py`:
```python
@lru_cache()
def get_my_service() -> MyService:
    repository = MyRepository(get_database_provider())
    return MyService(repository)
```

### Add Router
Create `app/api/routers/my_router.py`:
```python
router = APIRouter(prefix="/my", tags=["my"])

@router.get("/items")
async def get_items(service: MyService = Depends(get_my_service)):
    return await service.get_items()
```

Include in `app/main.py`:
```python
from app.api.routers.my_router import router as my_router
app.include_router(my_router)
```

## Scripts

### run.ps1
- `.\scripts\setup\run.ps1` - Build and start containers
- `.\scripts\setup\run.ps1 -Rebuild` - Force rebuild (no cache)
- `.\scripts\setup\run.ps1 -Start` - Start without rebuild

### db.ps1
- `.\scripts\setup\db.ps1 -Init` - Initialize database with migrations
- `.\scripts\setup\db.ps1 -Revision -Message "desc"` - Create new migration
- `.\scripts\setup\db.ps1 -Upgrade` - Apply migrations
- `.\scripts\setup\db.ps1 -Downgrade -Rev -1` - Rollback one migration
- `.\scripts\setup\db.ps1 -Backup` - Backup database to ./backups/
- `.\scripts\setup\db.ps1 -Restore -File backup.sql` - Restore from backup
- `.\scripts\setup\db.ps1 -Rebuild` - Drop and recreate database

### cleanup.ps1
- `.\scripts\cleanup.ps1` - Remove containers
- `.\scripts\cleanup.ps1 -Force` - Remove containers and images
- `.\scripts\cleanup.ps1 -Nuke` - Remove everything (containers, images, volumes)

### collect-logs.ps1
- `.\scripts\collect-logs.ps1` - Collect logs to ./logs/timestamp/
- `.\scripts\collect-logs.ps1 -Follow` - Stream live logs
- `.\scripts\collect-logs.ps1 -Reproduce` - Capture logs during request reproduction

### seed-template.ps1
- `.\scripts\db\seed-template.ps1` - Insert sample template data

## Services
- API: http://localhost:8000
- Database: PostgreSQL (port 5432)
- Cache: Redis (port 6379)
- Mail: MailHog UI (http://localhost:8025)

