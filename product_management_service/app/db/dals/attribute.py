from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from app.db.models import Attribute
from sqlalchemy.engine.row import Row, Sequence
from uuid import UUID


class AttributeDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_attribute(self, name: str, description: str) -> Attribute:
        new_attribute = Attribute(name=name.lower(), description=description)
        self.db_session.add(new_attribute)
        await self.db_session.flush()
        return new_attribute

    async def get_attribute_by_id(self, attribute_id: UUID) -> Optional[Attribute]:
        query = (select(Attribute).
                 where(Attribute.attribute_id == attribute_id))
        res = await self.db_session.execute(query)
        attribute = res.fetchone()
        if attribute:
            return attribute[0]

    async def get_attribute_by_name(self, name: str) -> Optional[Attribute]:
        query = (select(Attribute.attribute_id).
                 where(Attribute.name == name.lower()))
        res = await self.db_session.execute(query)
        attribute = res.fetchone()
        if attribute:
            return attribute[0]

    async def get_attributes(self) -> Optional[Sequence[Row[tuple[Attribute]]]]:
        query = select(Attribute)
        res = await self.db_session.execute(query)
        attributes = res.fetchall()
        if attributes:
            return attributes

    async def delete_attribute(self, attribute_id: UUID) -> Optional[UUID]:
        query = (delete(Attribute).
                 where(Attribute.attribute_id == attribute_id).
                 returning(Attribute.attribute_id))
        res = await self.db_session.execute(query)
        deleted_attribute_row = res.fetchone()
        if deleted_attribute_row:
            return deleted_attribute_row[0]

    async def update_attribute(self, attribute_id: UUID, **kwargs) -> Optional[Attribute]:
        query = (update(Attribute).
                 where(Attribute.attribute_id == attribute_id).
                 values(kwargs).
                 returning(Attribute))
        res = await self.db_session.execute(query)
        attribute = res.fetchone()
        if attribute:
            return attribute[0]

    async def attribute_already_exists(self, name: str) -> bool:
        attribute = await self.get_attribute_by_name(name)
        if attribute:
            return True
        return False
