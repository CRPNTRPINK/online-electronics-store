from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import CategoryAttributes, Category, Attribute
from sqlalchemy import delete


class CategoryAttributeDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_category_attribute(self, category: Category, attribute: Attribute) -> CategoryAttributes:
        new_category_attribute = CategoryAttributes(category=category, attribute=attribute)
        self.db_session.add(new_category_attribute)
        await self.db_session.flush()
        return new_category_attribute

    async def delete_category_attribute(self, category_attr_id: UUID) -> Optional[UUID]:
        query = (delete(CategoryAttributes).
                 where(CategoryAttributes.category_attribute_id == category_attr_id).
                 returning(CategoryAttributes.category_attribute_id))
        res = await self.db_session.execute(query)
        category_attr_id = res.fetchone()
        if category_attr_id:
            return category_attr_id[0]
