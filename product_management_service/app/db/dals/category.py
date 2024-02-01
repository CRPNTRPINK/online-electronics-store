from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.engine.row import Row, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Category


class CategoryDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_category(self, name: str, description: str) -> Category:
        new_category = Category(name=name.lower(), description=description)
        self.db_session.add(new_category)
        await self.db_session.flush()
        return new_category

    async def get_category_by_id(self, category_id: UUID) -> Optional[Category]:
        query = (select(Category).
                 where(Category.category_id == category_id))
        res = await self.db_session.execute(query)
        category = res.fetchone()
        if category:
            return category[0]

    async def get_category_by_name(self, name: str) -> Optional[Category]:
        query = (select(Category.category_id).
                 where(Category.name == name.lower()))
        res = await self.db_session.execute(query)
        category = res.fetchone()
        if category:
            return category[0]

    async def get_categories(self) -> Optional[Sequence[Row[tuple[Category]]]]:
        query = select(Category)
        res = await self.db_session.execute(query)
        categories = res.fetchall()
        if categories:
            return categories

    async def delete_category(self, category_id: UUID) -> Optional[UUID]:
        query = (delete(Category).
                           where(Category.category_id == category_id).
                           returning(Category.category_id))
        res = await self.db_session.execute(query)
        deleted_category_row = res.fetchone()
        if deleted_category_row:
            return deleted_category_row[0]

    async def update_category(self, category_id: UUID, **kwargs) -> Optional[Category]:
        query = (update(Category).
                 where(Category.category_id == category_id).
                 values(kwargs).
                 returning(Category))
        res = await self.db_session.execute(query)
        category = res.fetchone()
        if category:
            return category[0]

    async def category_already_exists(self, name: str):
        category = await self.get_category_by_name(name)
        if category:
            return True
        return False
