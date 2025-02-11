from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project

from .base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: AsyncSession):
        super().__init__(Project, db)
    
    async def get_active_projects(self):
        query = select(self.model).where(
            self.model.status == 'active'
        )
        result = await self.db.execute(query)
        return result.scalars().all()
