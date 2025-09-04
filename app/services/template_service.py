from typing import List, Optional

from app.data.repositories.template_repository import TemplateRepository
from app.services.cache_service import CacheService


class TemplateService:
    """Service for template business logic."""
    
    def __init__(self, repository: TemplateRepository, cache_service: CacheService):
        self.repository = repository
        self.cache_service = cache_service
    
    async def get_all_templates(self, use_cache: bool = True) -> dict:
        """Get all templates with optional caching."""
        cache_key = "test:template"
        
        # Try cache first if enabled
        if use_cache:
            cached_templates = await self.cache_service.get_templates_cache(cache_key)
            if cached_templates:
                return {"source": "redis", "templates": cached_templates}
        
        # Fetch from database
        templates = await self.repository.get_all()
        
        # Cache the result if caching is enabled
        if use_cache:
            await self.cache_service.set_templates_cache(cache_key, templates)
        
        return {"source": "db", "templates": templates}
    
    async def get_template_by_id(self, template_id: int) -> Optional[dict]:
        """Get template by ID."""
        return await self.repository.get_by_id(template_id)
    
    async def create_template(self, title: str, body: Optional[str] = None, status: str = "DRAFT") -> dict:
        """Create new template and invalidate cache."""
        template = await self.repository.create(title, body, status)
        
        # Invalidate cache since we have new data
        await self.cache_service.invalidate_cache("test:template")
        
        return template
