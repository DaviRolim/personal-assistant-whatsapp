from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get(self, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, where=None, limit=None, order_by=None) -> List[ModelType]:
        query = select(self.model)
        if where:
            query = query.where(*where)
        if order_by:
            query = query.order_by(*order_by)
        if limit:
            query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, id: Any, obj_in: dict) -> Optional[ModelType]:
        query = update(self.model).where(self.model.id == id).values(**obj_in)
        await self.db.execute(query)
        await self.db.commit()
        return await self.get(id)

    async def delete(self, id: Any) -> bool:
        query = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
        await self.db.commit()
        return result.rowcount > 0
