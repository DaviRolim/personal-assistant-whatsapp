from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.split_me_later import Task
from .base_repository import BaseRepository

class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: Session):
        super().__init__(Task, db)
    
    async def get_by_project(self, project_id: int):
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_subtasks(self, parent_task_id: int):
        query = select(self.model).where(self.model.parent_task_id == parent_task_id)
        result = await self.db.execute(query)
        return result.scalars().all()
