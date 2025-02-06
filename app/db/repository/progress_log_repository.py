from sqlalchemy import select

from app.models.progress_log import ProgressLog
from .base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession

class ProgressLogRepository(BaseRepository[ProgressLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProgressLog, db)
    
    async def get_by_task(self, task_id: int):
        query = select(self.model).where(self.model.related_task_id == task_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_goal(self, goal_id: int):
        query = select(self.model).where(self.model.related_goal_id == goal_id)
        result = await self.db.execute(query)
        return result.scalars().all()
