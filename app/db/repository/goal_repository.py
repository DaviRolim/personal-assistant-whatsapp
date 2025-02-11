from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal import Goal

from .base_repository import BaseRepository


class GoalRepository(BaseRepository[Goal]):
    def __init__(self, db: AsyncSession):
        super().__init__(Goal, db)
    
    async def get_active_goals(self):
        query = select(self.model).where(
            self.model.status == 'active'
        )
        result = await self.db.execute(query)
        return result.scalars().all()
