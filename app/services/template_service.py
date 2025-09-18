from typing import List, Optional
from uuid import UUID

from app.data.repositories.template_repository import TemplateRepository
from app.services.cache_service import CacheService
from app.data.schemas.models import TemplateItem
from app.data.DTO.template_dto import (
    TemplateCreateRequest, 
    TemplateUpdateRequest, 
    TemplateResponse, 
    TemplateListResponse,
    TemplateCreateResponse
)


class TemplateService:
    """Service for template business logic."""
    
    def __init__(self, repository: TemplateRepository, cache_service: CacheService):
        self.repository = repository
        self.cache_service = cache_service
    
    async def get_all_templates(self, use_cache: bool = True, limit: int = 100, offset: int = 0) -> TemplateListResponse:
        """Get all templates with optional caching."""
        cache_key = "test:template"
        
        # Try cache first if enabled
        if use_cache:
            cached_templates = await self.cache_service.get_templates_cache(cache_key)
            if cached_templates:
                templates = [TemplateResponse.model_validate(t) for t in cached_templates]
                return TemplateListResponse(
                    source="redis",
                    templates=templates,
                    total=len(templates),  # Set total from cached data
                    limit=limit,
                    offset=offset
                )
        
        # Fetch from database using base repository
        template_entities = await self.repository.get_all(limit=limit, offset=offset)
        
        # Convert to response DTOs
        templates = [TemplateResponse.model_validate(template) for template in template_entities]
        
        # Cache the result if caching is enabled
        if use_cache:
            template_dicts = [template.model_dump() for template in templates]
            await self.cache_service.set_templates_cache(cache_key, template_dicts)
        
        return TemplateListResponse(
            source="db",
            templates=templates,
            total=len(templates),
            limit=limit,
            offset=offset
        )
    
    async def get_template_by_id(self, template_id: UUID) -> Optional[TemplateResponse]:
        """Get template by ID."""
        template = await self.repository.get_by_id(template_id)
        return TemplateResponse.model_validate(template) if template else None
    
    async def create_template(self, create_request: TemplateCreateRequest) -> TemplateCreateResponse:
        """Create new template using DTO and base repository."""
        # Create entity from DTO
        template_entity = TemplateItem(
            title=create_request.title,
            body=create_request.body,
            status=create_request.status
        )
        
        # Use base repository create method
        created_template = await self.repository.create(template_entity)
        
        # Invalidate cache since we have new data
        await self.cache_service.invalidate_cache("test:template")
        
        # Return response DTO
        return TemplateCreateResponse(
            message="Template created successfully",
            template=TemplateResponse.model_validate(created_template)
        )
    
    async def update_template(self, template_id: UUID, update_request: TemplateUpdateRequest) -> Optional[TemplateResponse]:
        """Update template using DTO."""
        # Convert DTO to dict, excluding None values
        update_data = update_request.model_dump(exclude_none=True)
        
        if not update_data:
            # No fields to update
            return await self.get_template_by_id(template_id)
        
        # Add updated_at timestamp to update data
        from datetime import datetime
        update_data['updated_at'] = datetime.utcnow()
        
        try:
            updated_template = await self.repository.update_by_id(template_id, update_data)
            
            # Invalidate cache
            await self.cache_service.invalidate_cache("test:template")
            
            return TemplateResponse.model_validate(updated_template)
        except ValueError:
            # Template not found
            return None
    
    async def delete_template(self, template_id: UUID) -> bool:
        """Delete template by ID."""
        result = await self.repository.delete_by_id(template_id)
        
        if result:
            # Invalidate cache
            await self.cache_service.invalidate_cache("test:template")
        
        return result
    
    async def find_templates_by_status(self, status: str) -> List[TemplateResponse]:
        """Find templates by status."""
        templates = await self.repository.find_by_status(status)
        return [TemplateResponse.model_validate(template) for template in templates]
