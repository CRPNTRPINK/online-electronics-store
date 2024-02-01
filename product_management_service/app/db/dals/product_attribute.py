from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from app.db.models import ProductAttributeValues, Product, Attribute


class ProductAttributeDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_product_attribute(self, product: Product, attribute: Attribute, value) -> ProductAttributeValues:
        new_product_attribute = ProductAttributeValues(product=product, attribute=attribute, value=value)
        self.db_session.add(new_product_attribute)
        await self.db_session.flush()
        return new_product_attribute

    async def delete_product_attribute(self, product_attr_id: UUID) -> Optional[UUID]:
        query = (delete(ProductAttributeValues).
                 where(ProductAttributeValues.product_attribute_id == product_attr_id).
                 returning(ProductAttributeValues.product_attribute_id))
        res = await self.db_session.execute(query)
        product_attr_id = res.fetchone()
        if product_attr_id:
            return product_attr_id[0]