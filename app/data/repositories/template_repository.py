from typing import List
from uuid import UUID

from app.core.database import DatabaseProvider
from app.data.repositories.base_repository import BaseRepository
from app.data.schemas.models import TemplateItem


class TemplateRepository(BaseRepository[TemplateItem]):
    """Repository for template item data operations."""
    
    def __init__(self, db_provider: DatabaseProvider):
        super().__init__(db_provider, TemplateItem)
    
    async def find_by_status(self, status: str) -> List[TemplateItem]:
        """Find templates by status."""
        return await self.find_all(status=status)
