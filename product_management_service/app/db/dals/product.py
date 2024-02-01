from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.engine.row import Row, Sequence
from sqlalchemy.orm import joinedload
from app.db.models import Product, Category


class ProductDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_product(
            self,
            name: str,
            description: str,
            price: float,
            stock_quantity: int,
            category: Category,
            manufacturer: str) -> Product:
        new_product = Product(
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            category=category,
            manufacturer=manufacturer.lower()
        )
        self.db_session.add(new_product)
        await self.db_session.flush()
        return new_product

    async def get_product_by_id(self, product_id: UUID) -> Optional[Product]:
        query = (select(Product).
                 where(Product.product_id == product_id))
        res = await self.db_session.execute(query)
        product = res.fetchone()
        if product:
            return product[0]

    async def get_products(self, page: int = 1, limit: int = 10) -> Optional[Sequence[Row[tuple[Product]]]]:
        offset = (page - 1) * limit
        query = select(Product).limit(limit).offset(offset)
        res = await self.db_session.execute(query)
        products = res.fetchall()
        if products:
            return products

    async def update_product(self, product_id: UUID, **kwargs) -> Optional[Product]:
        query = (update(Product).
                 where(Product.product_id == product_id).
                 values(kwargs).
                 returning(Product.product_id))
        res = await self.db_session.execute(query)
        product_id = res.fetchone()
        if product_id:
            product = await self.get_product_by_id(product_id=product_id[0])
            return product

    async def delete_product(self, product_id: UUID) -> Optional[UUID]:
        query = (delete(Product).
                 where(Product.product_id == product_id).
                 returning(Product.product_id))
        res = await self.db_session.execute(query)
        deleted_product_id = res.fetchone()
        if deleted_product_id:
            return deleted_product_id[0]
