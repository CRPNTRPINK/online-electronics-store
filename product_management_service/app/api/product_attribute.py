from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.row import Row
from app.db.session import get_db
from app.db.dals.product import ProductDAL
from app.db.dals.attribute import AttributeDAL
from app.db.dals.product_attribute import ProductAttributeDAL
from app.db.models import ProductAttributeValues
from app.schemas.product_attributes import (ProductAttributeRequest,
                                            ProductAttributeResponse,
                                            DeleteProductAttributeResponse)

product_attr_router = APIRouter(prefix="/product-attribute", tags=["product-attribute"])


async def _create_product_attribute(body: ProductAttributeRequest, db: AsyncSession) -> ProductAttributeValues:
    async with db as session:
        async with session.begin():
            product = await ProductDAL(db_session=db).get_product_by_id(product_id=body.product_id)
            attribute = await AttributeDAL(db_session=db).get_attribute_by_id(attribute_id=body.attribute_id)
            product_attr_dal = ProductAttributeDAL(db_session=db)
            product_attribute = await product_attr_dal.create_product_attribute(
                product=product,
                attribute=attribute,
                value=body.value
            )
            return product_attribute


async def _delete_product_attribute(product_attr_id: UUID, db: AsyncSession) -> Optional[UUID]:
    async with db as session:
        async with session.begin():
            product_attr_dal = ProductAttributeDAL(db_session=db)
            deleted_product_attr_id = await product_attr_dal.delete_product_attribute(product_attr_id)
            if not deleted_product_attr_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ProductAttributeValue с product_attribute_id: {product_attr_id} не найден"
                )
            return deleted_product_attr_id


@product_attr_router.post("/",
                          description="Создать связь между продуктом и атрибутом",
                          response_model=ProductAttributeResponse)
async def create_product_attribute(body: ProductAttributeRequest, db: AsyncSession = Depends(get_db)):
    try:
        product_attribute = await _create_product_attribute(body, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return ProductAttributeResponse.model_validate(product_attribute)


@product_attr_router.delete("/",
                            description="Удалить связь между продуктом и атрибутом",
                            response_model=DeleteProductAttributeResponse)
async def delete_product_attribute(product_attribute_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        product_attribute_id = await _delete_product_attribute(product_attribute_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return DeleteProductAttributeResponse.model_validate(product_attribute_id)
