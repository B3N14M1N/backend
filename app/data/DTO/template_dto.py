from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.data.schemas.models import TemplateStatus


class TemplateCreateRequest(BaseModel):
    """DTO for creating a new template."""
    title: str = Field(..., min_length=1, max_length=200, description="Template title")
    body: Optional[str] = Field(None, description="Template body content")
    status: TemplateStatus = Field(TemplateStatus.DRAFT, description="Template status")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My Template",
                "body": "This is the template content",
                "status": "DRAFT"
            }
        }


class TemplateUpdateRequest(BaseModel):
    """DTO for updating an existing template."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Template title")
    body: Optional[str] = Field(None, description="Template body content")
    status: Optional[TemplateStatus] = Field(None, description="Template status")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Template",
                "body": "Updated content",
                "status": "PUBLISHED"
            }
        }


class TemplateResponse(BaseModel):
    """DTO for template responses."""
    id: UUID
    title: str
    body: Optional[str]
    status: TemplateStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "My Template",
                "body": "This is the template content",
                "status": "DRAFT",
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-01T12:00:00Z"
            }
        }


class TemplateListResponse(BaseModel):
    """DTO for template list responses with metadata."""
    source: str = Field(description="Data source (db or redis)")
    templates: list[TemplateResponse]
    total: Optional[int] = Field(None, description="Total count if available")
    limit: Optional[int] = Field(None, description="Applied limit")
    offset: Optional[int] = Field(None, description="Applied offset")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "db",
                "templates": [],
                "total": 10,
                "limit": 20,
                "offset": 0
            }
        }


class TemplateCreateResponse(BaseModel):
    """DTO for template creation response."""
    message: str
    template: TemplateResponse

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Template created successfully",
                "template": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "My Template",
                    "body": "Content",
                    "status": "DRAFT",
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z"
                }
            }
        }