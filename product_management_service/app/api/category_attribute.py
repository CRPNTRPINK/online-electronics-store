from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.category_attributes import (CategoryAttributesRequest,
                                             CategoryAttributesResponse,
                                             DeleteCategoryAttributeResponse)
from app.db.dals.category_attribute import CategoryAttributeDAL
from app.db.models import CategoryAttributes
from app.db.dals.category import CategoryDAL
from app.db.dals.attribute import AttributeDAL

category_attr_router = APIRouter(prefix="/category-attribute", tags=["category-attribute"])


async def _create_category_attribute(body: CategoryAttributesRequest, db: AsyncSession) -> CategoryAttributes:
    async with db as session:
        async with session.begin():
            category = await CategoryDAL(db).get_category_by_id(category_id=body.category_id)
            attribute = await AttributeDAL(db).get_attribute_by_id(attribute_id=body.attribute_id)
            category_attr_dal = CategoryAttributeDAL(session)
            category_att = await category_attr_dal.create_category_attribute(
                category=category,
                attribute=attribute
            )
            return category_att


async def _delete_category_attribute(category_attr_id: UUID, db: AsyncSession) -> Optional[UUID]:
    async with db as session:
        async with session.begin():
            category_attr_dal = CategoryAttributeDAL(session)
            deleted_category_attr_id = await category_attr_dal.delete_category_attribute(
                category_attr_id=category_attr_id
            )
            if not deleted_category_attr_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"CategoryAttribute с category_attribute_id: {category_attr_id} не найден"
                )
            return deleted_category_attr_id


@category_attr_router.post("/",
                           description="Создать связь между категорией и атрибутом",
                           response_model=CategoryAttributesResponse)
async def create_category_attribute(body: CategoryAttributesRequest, db: AsyncSession = Depends(get_db)):
    try:
        category_attribute = await _create_category_attribute(body, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return CategoryAttributesResponse.model_validate(category_attribute)


@category_attr_router.delete("/",
                             description="Удалить связь между категорией и атрибутом",
                             response_model=DeleteCategoryAttributeResponse)
async def delete_category_attribute(category_attribute_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        category_attribute_id = await _delete_category_attribute(category_attribute_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return DeleteCategoryAttributeResponse.model_validate(category_attribute_id)
