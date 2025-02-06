from sqlalchemy import select

from app.models.goal import Goal
from .base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
class GoalRepository(BaseRepository[Goal]):
    def __init__(self, db: AsyncSession):
        super().__init__(Goal, db)
    
    async def get_by_user(self, user_id: int):
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_active_goals(self, user_id: int):
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.status == 'active'
        )
        result = await self.db.execute(query)
        return result.scalars().all()
