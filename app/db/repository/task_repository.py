from sqlalchemy import select

from app.models.task import Task
from .base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)
    
    async def get_by_project(self, project_id: int):
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_subtasks(self, parent_task_id: int):
        query = select(self.model).where(self.model.parent_task_id == parent_task_id)
        result = await self.db.execute(query)
        return result.scalars().all()
