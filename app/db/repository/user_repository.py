from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from .base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    async def get_by_whatsapp(self, whatsapp_number: str) -> User:
        query = select(self.model).where(self.model.whatsapp_number == whatsapp_number)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_last_active(self, user_id: int) -> User:
        return await self.update(user_id, {"last_active": "CURRENT_TIMESTAMP"})
