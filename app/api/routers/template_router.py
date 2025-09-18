from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from uuid import UUID

from app.services.template_service import TemplateService
from app.core.dependencies import get_template_service
from app.data.DTO.template_dto import (
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplateResponse,
    TemplateListResponse,
    TemplateCreateResponse
)

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/template", response_model=TemplateListResponse)
async def get_templates(
    limit: int = Query(100, ge=1, le=500, description="Maximum number of templates to return"),
    offset: int = Query(0, ge=0, description="Number of templates to skip"),
    use_cache: bool = Query(True, description="Whether to use cache"),
    template_service: TemplateService = Depends(get_template_service)
):
    """Return list of template items with pagination; optionally cache result in redis for 30s."""
    try:
        result = await template_service.get_all_templates(
            use_cache=use_cache, 
            limit=limit, 
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch templates: {str(e)}")


@router.get("/template/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    template_service: TemplateService = Depends(get_template_service)
):
    """Get a specific template by ID."""
    try:
        template = await template_service.get_template_by_id(template_id)
        if template is None:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch template: {str(e)}")


@router.post("/template", response_model=TemplateCreateResponse, status_code=201)
async def create_template(
    create_request: TemplateCreateRequest,
    template_service: TemplateService = Depends(get_template_service)
):
    """Create a new template item."""
    try:
        result = await template_service.create_template(create_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.put("/template/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    update_request: TemplateUpdateRequest,
    template_service: TemplateService = Depends(get_template_service)
):
    """Update an existing template."""
    try:
        template = await template_service.update_template(template_id, update_request)
        if template is None:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")


@router.delete("/template/{template_id}", status_code=204)
async def delete_template(
    template_id: UUID,
    template_service: TemplateService = Depends(get_template_service)
):
    """Delete a template by ID."""
    try:
        result = await template_service.delete_template(template_id)
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")


@router.get("/template/status/{status}", response_model=list[TemplateResponse])
async def get_templates_by_status(
    status: str,
    template_service: TemplateService = Depends(get_template_service)
):
    """Get templates filtered by status."""
    try:
        templates = await template_service.find_templates_by_status(status)
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch templates by status: {str(e)}")
