from __future__ import annotations
from typing import Optional
from enum import Enum as PyEnum
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

# Helpers
def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class TemplateStatus(str, PyEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"

class TemplateItem(SQLModel, table=True):
    __tablename__ = "templateitem"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, nullable=False)
    body: Optional[str] = None
    status: TemplateStatus = Field(default=TemplateStatus.DRAFT)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
