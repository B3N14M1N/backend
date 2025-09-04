from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.services.template_service import TemplateService
from app.core.dependencies import get_template_service

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/template")
async def get_templates(
    template_service: TemplateService = Depends(get_template_service)
):
    """Return list of template items; cache result in redis for 30s."""
    try:
        result = await template_service.get_all_templates()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch templates: {str(e)}")


@router.get("/template/{template_id}")
async def get_template(
    template_id: int,
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


@router.post("/template")
async def create_template(
    title: str,
    body: Optional[str] = None,
    status: str = "DRAFT",
    template_service: TemplateService = Depends(get_template_service)
):
    """Create a new template item."""
    try:
        template = await template_service.create_template(title, body, status)
        return {"message": "Template created successfully", "template": template}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")
