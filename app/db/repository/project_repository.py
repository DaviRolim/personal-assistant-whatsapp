from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.split_me_later import Project
from .base_repository import BaseRepository

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)
    
    async def get_by_user(self, user_id: int):
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_active_projects(self, user_id: int):
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.status == 'active'
        )
        result = await self.db.execute(query)
        return result.scalars().all()
