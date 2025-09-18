from __future__ import annotations
from typing import Optional
from enum import Enum as PyEnum
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

# Helpers
def utcnow() -> datetime:
    """Return current UTC time as timezone-naive datetime for database compatibility."""
    return datetime.utcnow()

class TemplateStatus(str, PyEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"

class TemplateItem(SQLModel, table=True):
    __tablename__ = "templateitem"
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=200, nullable=False)
    body: Optional[str] = None
    status: TemplateStatus = Field(default=TemplateStatus.DRAFT)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
