from typing import Optional, List
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ProductImage, Product


class ProductImageDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def upload_image(self, image_name: str, description: str, product: Product) -> ProductImage:
        new_image = ProductImage(
            image_name=image_name,
            description=description,
            product=product
        )
        self.db_session.add(new_image)
        return new_image

    async def delete_image(self, image_id: UUID) -> Optional[str]:
        query = (delete(ProductImage).
                 where(ProductImage.image_id == image_id).
                 returning(ProductImage.image_name))
        res = await self.db_session.execute(query)
        image_id = res.fetchone()
        if image_id:
            return image_id[0]

