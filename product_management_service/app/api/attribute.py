from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.row import Row
from app.schemas.attribute import AttributeRequest, AttributeResponse, DeleteAttributeResponse, UpdateAttributeRequest
from app.db.dals.attribute import AttributeDAL
from app.db.session import get_db
from app.db.models import (
    Attribute
)

attribute_router = APIRouter(prefix="/attribute", tags=["attribute"])


async def _create_attribute(body: AttributeRequest, db: AsyncSession) -> Optional[Attribute]:
    async with db as session:
        async with session.begin():
            attribute_dal = AttributeDAL(session)
            if await attribute_dal.attribute_already_exists(body.name):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail=f'Атрибут с именем "{body.name}" уже существует')
            attribute = await attribute_dal.create_attribute(
                name=body.name,
                description=body.description
            )
            return attribute


async def _get_attribute_by_id(attribute_id: UUID, db: AsyncSession) -> Optional[Attribute]:
    async with db as session:
        async with session.begin():
            attribute_dal = AttributeDAL(session)
            attribute = await attribute_dal.get_attribute_by_id(attribute_id=attribute_id)

            if not attribute:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Атрибут с attribute_id: {attribute_id} не найден"
                )
            return attribute


async def _get_attributes(db: AsyncSession) -> Optional[List[Row[Attribute]]]:
    async with db as session:
        async with session.begin():
            attribute_dal = AttributeDAL(session)
            attributes = await attribute_dal.get_attributes()
            if not attributes:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Атрибутов нет")
            return attributes


async def _delete_attribute(attribute_id: UUID, db: AsyncSession) -> Optional[UUID]:
    async with db as session:
        async with session.begin():
            attribute_dal = AttributeDAL(session)
            deleted_attr_id = await attribute_dal.delete_attribute(attribute_id=attribute_id)
            if not deleted_attr_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Атрибут с attribute_id: {attribute_id} не найден"
                )
            return deleted_attr_id


async def _update_attribute(attribute_id: UUID, body: UpdateAttributeRequest, db: AsyncSession) -> Optional[Attribute]:
    body = body.model_dump(exclude_none=True)
    if not body:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Должен быть указан хотя бы один параметр для информации об обновлении атрибута")
    async with db as session:
        async with session.begin():
            attribute_dal = AttributeDAL(session)
            attribute = await attribute_dal.update_attribute(attribute_id=attribute_id, **body)
            if not attribute:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Атрибут с attribute_id: {attribute_id} не найден"
                )
            return attribute


@attribute_router.post("/", description="Создать атрибут", response_model=AttributeResponse)
async def create_attribute(body: AttributeRequest, db: AsyncSession = Depends(get_db)):
    try:
        attribute = await _create_attribute(body, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return AttributeResponse.model_validate(attribute)


@attribute_router.get("/get-attributes/", description="получить все атрибуты", response_model=List[AttributeResponse])
async def get_attributes(db: AsyncSession = Depends(get_db)):
    try:
        attributes = await _get_attributes(db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return [AttributeResponse.model_validate(attribute[0]) for attribute in attributes]


@attribute_router.get("/get-attribute-by-id/", description="получить атрибут по id", response_model=AttributeResponse)
async def get_attribute_by_id(attribute_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        attribute = await _get_attribute_by_id(attribute_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return AttributeResponse.model_validate(attribute)


@attribute_router.delete("/", description="Удалить атрибут", response_model=DeleteAttributeResponse)
async def delete_attribute(attribute_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        attribute_id = await _delete_attribute(attribute_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return DeleteAttributeResponse(attribute_id=attribute_id)


@attribute_router.put("/", description="Обновить атрибут", response_model=AttributeResponse)
async def update_attribute(attribute_id: UUID, body: UpdateAttributeRequest, db: AsyncSession = Depends(get_db)):
    try:
        attribute = await update_attribute(attribute_id, body)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return attribute
