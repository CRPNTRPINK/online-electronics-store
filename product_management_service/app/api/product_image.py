import os
import shutil
import uuid
from typing import Optional

from app.db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.row import Row
from app.db.dals.product_image import ProductImageDAL
from app.db.dals.product import ProductDAL
from app.db.models import ProductImage
from app.schemas.product_image import ProductImageResponse, DeleteProductImageResponse
from uuid import UUID
from app.utils.image_utils import save_image, remove_image

image_router = APIRouter(prefix="/image", tags=["image"])


async def _create_image(image_name: str, description: str, product_id: UUID, db: AsyncSession) -> ProductImage:
    async with db as session:
        async with session.begin():
            product_image_dal = ProductImageDAL(db_session=db)
            product = await ProductDAL(db_session=db).get_product_by_id(product_id=product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Продукт с id "{product_id}" не найден'
                )
            product_image = await product_image_dal.upload_image(
                image_name=image_name,
                description=description,
                product=product
            )
            return product_image


async def _delete_image(image_id: UUID, db: AsyncSession) -> Optional[str]:
    async with db as session:
        async with session.begin():
            product_image_dal = ProductImageDAL(db_session=db)
            deleted_image_name = await product_image_dal.delete_image(image_id=image_id)
            if not deleted_image_name:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Картинка с image_id: {image_id} не найдена"
                )
            remove_image(deleted_image_name)
            return deleted_image_name


@image_router.post("/upload-image/", description="Загрузить картинку для продукта", response_model=ProductImageResponse)
async def upload_image(description: str = Body(..., min_length=5, max_length=50),
                       product_id: UUID = Body(...),
                       file: UploadFile = File(...),
                       db: AsyncSession = Depends(get_db)):
    image_name = ''
    try:
        image_name = save_image(file)
        image = await _create_image(image_name=image_name, description=description, product_id=product_id, db=db)
    except HTTPException as er:
        if image_name:
            remove_image(image_name)
        raise er
    except Exception as er:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=er.args[-1])
    return ProductImageResponse.model_validate(image)


@image_router.delete("/", description="Удалить картинку", response_model=DeleteProductImageResponse)
async def delete_image(image_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        image_name = await _delete_image(image_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=er.args[-1])
    return DeleteProductImageResponse(image_name=image_name)
