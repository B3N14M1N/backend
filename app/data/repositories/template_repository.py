from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import DatabaseProvider


class TemplateRepository:
    """Repository for template item data operations."""
    
    def __init__(self, db_provider: DatabaseProvider):
        self.db_provider = db_provider
    
    async def get_all(self) -> List[dict]:
        """Get all template items."""
        async with self.db_provider.get_session() as session:
            result = await session.execute(
                text("SELECT id, title, status, created_at FROM templateitem ORDER BY id")
            )
            rows = result.fetchall()
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "status": row[2],
                    "created_at": str(row[3])
                }
                for row in rows
            ]
    
    async def get_by_id(self, template_id: int) -> Optional[dict]:
        """Get template item by ID."""
        async with self.db_provider.get_session() as session:
            result = await session.execute(
                text("SELECT id, title, status, created_at FROM templateitem WHERE id = :id"),
                {"id": template_id}
            )
            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "title": row[1],
                    "status": row[2],
                    "created_at": str(row[3])
                }
            return None
    
    async def create(self, title: str, body: Optional[str] = None, status: str = "DRAFT") -> dict:
        """Create new template item."""
        async with self.db_provider.get_session() as session:
            result = await session.execute(
                text("""
                    INSERT INTO templateitem (title, body, status, created_at, updated_at)
                    VALUES (:title, :body, :status, now(), now())
                    RETURNING id, title, status, created_at
                """),
                {"title": title, "body": body, "status": status}
            )
            row = result.fetchone()
            return {
                "id": row[0],
                "title": row[1],
                "status": row[2],
                "created_at": str(row[3])
            }
