from functools import lru_cache

from app.core.database import get_db_provider, DatabaseProvider
from app.data.repositories.template_repository import TemplateRepository
from app.services.cache_service import CacheService
from app.services.template_service import TemplateService


@lru_cache()
def get_database_provider() -> DatabaseProvider:
    """Get database provider dependency."""
    return get_db_provider()


@lru_cache()
def get_template_repository() -> TemplateRepository:
    """Get template repository dependency."""
    db_provider = get_database_provider()
    return TemplateRepository(db_provider)


@lru_cache()
def get_cache_service() -> CacheService:
    """Get cache service dependency."""
    return CacheService()


@lru_cache()
def get_template_service() -> TemplateService:
    """Get template service dependency."""
    repository = get_template_repository()
    cache_service = get_cache_service()
    return TemplateService(repository, cache_service)
