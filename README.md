# FastAPI Backend Template

FastAPI template with async PostgreSQL, Redis caching, dependency injection, and clean architecture.

## Project Structure

```
app/
├── api/routers/           # API endpoints with DTO-based request/response models
├── core/                  # Infrastructure (database, dependencies, config)
├── data/
│   ├── DTO/              # Data Transfer Objects (request/response models)
│   ├── repositories/     # Data access layer with base repository pattern
│   └── schemas/          # Database models (SQLModel entities)
└── services/             # Business logic with DTO transformations
```

## Quick Start

```powershell
.\scripts\setup\run.ps1              # Build and start with cached images
.\scripts\setup\db.ps1 -Init         # Initialize database
.\scripts\db\seed-template.ps1       # Seed sample data
```

Access API at http://localhost:8000/docs

**Tip:** Subsequent runs use cached builds for faster startup. Use `-NoCache` if you've changed dependencies.

## How to Extend

### Add Database Model
1. Define model in `app/data/schemas/models.py` using SQLModel with UUID primary key:
```python
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class MyModel(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    # other fields...
```
2. Create migration: `.\scripts\setup\db.ps1 -Revision -Message "add model"`
3. Apply migration: `.\scripts\setup\db.ps1 -Upgrade`

### Add Repository
Create `app/data/repositories/my_repository.py` extending BaseRepository:
```python
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.models import MyModel
from app.core.database import DatabaseProvider

class MyRepository(BaseRepository[MyModel]):
    def __init__(self, db_provider: DatabaseProvider):
        super().__init__(db_provider, MyModel)
    
    # Inherit all CRUD operations (create, get_by_id, get_all, update, delete_by_id, etc.)
    # Add custom methods as needed:
    async def find_by_name(self, name: str) -> List[MyModel]:
        return await self.find_all(name=name)  # Using enhanced find_all with criteria
```

### Add DTOs
Create `app/data/DTO/my_dto.py` for request/response models:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class MyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class MyUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None

class MyResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Add Service
Create `app/services/my_service.py` with DTO transformations:
```python
from uuid import UUID
from typing import Optional, List
from app.data.schemas.models import MyModel
from app.data.DTO.my_dto import MyCreateRequest, MyUpdateRequest, MyResponse

class MyService:
    def __init__(self, repository: MyRepository):
        self.repository = repository
    
    async def get_items(self, limit: int = 100, offset: int = 0) -> List[MyResponse]:
        items = await self.repository.get_all(limit=limit, offset=offset)
        return [MyResponse.model_validate(item) for item in items]
    
    async def get_item_by_id(self, item_id: UUID) -> Optional[MyResponse]:
        item = await self.repository.get_by_id(item_id)
        return MyResponse.model_validate(item) if item else None
    
    async def create_item(self, create_request: MyCreateRequest) -> MyResponse:
        # Convert DTO to entity
        item_entity = MyModel(
            name=create_request.name,
            description=create_request.description
        )
        
        # Use base repository create method
        created_item = await self.repository.create(item_entity)
        
        # Return response DTO
        return MyResponse.model_validate(created_item)
    
    async def update_item(self, item_id: UUID, update_request: MyUpdateRequest) -> Optional[MyResponse]:
        update_data = update_request.model_dump(exclude_none=True)
        if not update_data:
            return await self.get_item_by_id(item_id)
        
        try:
            updated_item = await self.repository.update_by_id(item_id, update_data)
            return MyResponse.model_validate(updated_item)
        except ValueError:
            return None
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
Create `app/api/routers/my_router.py` with DTO-based endpoints:
```python
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
from app.data.DTO.my_dto import MyCreateRequest, MyUpdateRequest, MyResponse

router = APIRouter(prefix="/my", tags=["my"])

@router.get("/items", response_model=List[MyResponse])
async def get_items(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: MyService = Depends(get_my_service)
):
    return await service.get_items(limit=limit, offset=offset)

@router.get("/items/{item_id}", response_model=MyResponse)
async def get_item(item_id: UUID, service: MyService = Depends(get_my_service)):
    item = await service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/items", response_model=MyResponse, status_code=201)
async def create_item(
    create_request: MyCreateRequest,
    service: MyService = Depends(get_my_service)
):
    return await service.create_item(create_request)

@router.put("/items/{item_id}", response_model=MyResponse)
async def update_item(
    item_id: UUID,
    update_request: MyUpdateRequest,
    service: MyService = Depends(get_my_service)
):
    item = await service.update_item(item_id, update_request)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

## DTO Architecture

This project follows a clean separation between database entities and API contracts using Data Transfer Objects (DTOs).

### DTO Structure
- **Request DTOs**: Input validation and data coming into the API
- **Response DTOs**: Standardized output format for API responses  
- **Domain Models**: Database entities (SQLModel) separate from API contracts

### Benefits
- **Type Safety**: Pydantic validation for all API inputs/outputs
- **API Stability**: Changes to database schema don't break API contracts
- **Clear Contracts**: Explicit definition of what data is expected/returned
- **Input Validation**: Automatic validation of request data with helpful error messages
- **Documentation**: Auto-generated OpenAPI schemas with examples

### Best Practices
1. **Never expose database models directly** in API endpoints
2. **Use specific DTOs** for different operations (Create vs Update vs Response)
3. **Include validation rules** and examples in DTO definitions
4. **Transform at service layer** between DTOs and domain models
5. **Use `exclude_none=True`** when converting update DTOs to avoid overwriting with null values

## Repository Architecture

This project uses a base repository pattern that provides common CRUD operations for all entities. The `BaseRepository<T>` class offers:

### Built-in Operations
- `create(entity: T)` - Create new entity
- `get_by_id(id: UUID)` / `find_by_id(id: UUID)` - Get entity by ID
- `get_all(limit, offset)` - Get all entities with pagination (no filtering)
- `find_all(limit, offset, **criteria)` - Find entities with optional filtering and pagination
- `update(entity: T)` - Update existing entity
- `update_by_id(id: UUID, update_data: dict)` - Update entity by ID with data
- `delete_by_id(id: UUID)` - Delete entity by ID
- `exists(id: UUID)` - Check if entity exists
- `find_by_criteria(**criteria)` - Find entities by field criteria (alias for find_all)

### Usage Example
```python
# All repositories inherit these operations
template_repo = TemplateRepository(db_provider)

# Basic CRUD
template = await template_repo.get_by_id(uuid)
all_templates = await template_repo.get_all(limit=10)
await template_repo.delete_by_id(uuid)

# Filtering with find_all (more flexible)
published = await template_repo.find_all(status="PUBLISHED")
recent_drafts = await template_repo.find_all(status="DRAFT", limit=5)

# Alternative syntax for filtering
published = await template_repo.find_by_criteria(status="PUBLISHED")
```

Include in `app/main.py`:
```python
from app.api.routers.my_router import router as my_router
app.include_router(my_router)
```

## Development Workflow

When making code changes to the FastAPI application:
```powershell
# After modifying Python code (fast rebuild with cache)
.\scripts\setup\run.ps1 -Build

# After changing dependencies in requirements.txt (full rebuild without cache)
.\scripts\setup\run.ps1 -Rebuild -NoCache

# Quick restart with cached build
.\scripts\setup\run.ps1
```

## Scripts

**Note:** The run.ps1 script now reuses PostgreSQL, Redis, and MailHog images by default to avoid unnecessary downloads. Use `-NoCache` when dependencies change to force a complete rebuild.

### run.ps1
- `.\scripts\setup\run.ps1` - Build and start containers (with cache)
- `.\scripts\setup\run.ps1 -Rebuild` - Full rebuild (removes containers/volumes, with cache)
- `.\scripts\setup\run.ps1 -Start` - Start without rebuild (only containers)
- `.\scripts\setup\run.ps1 -Build` - Rebuild only backend image/container (with cache)
- `.\scripts\setup\run.ps1 -NoCache` - Disable build cache (use with other commands)
- `.\scripts\setup\run.ps1 -Rebuild -NoCache` - Full rebuild without cache (for dependency changes)

### db.ps1
- `.\scripts\setup\db.ps1 -Init` - Initialize database with migrations
- `.\scripts\setup\db.ps1 -Revision -Message "<description>"` - Create new migration
- `.\scripts\setup\db.ps1 -Upgrade` - Apply migrations
- `.\scripts\setup\db.ps1 -Downgrade -Rev -1` - Rollback one migration
- `.\scripts\setup\db.ps1 -Backup` - Backup database to ./backups/
- `.\scripts\setup\db.ps1 -Restore -File backup.sql` - Restore from backup
- `.\scripts\setup\db.ps1 -Rebuild` - Drop and recreate database

### cleanup.ps1
- `.\scripts\cleanup.ps1` - Remove containers
- `.\scripts\cleanup.ps1 -Force` - Remove containers and images (keeps db volume)
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

