from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.row import Row, Sequence
from app.db.session import get_db
from app.db.dals.product import ProductDAL
from app.db.dals.category import CategoryDAL
from app.db.models import Product
from app.schemas.product import ProductRequest, ProductResponse, UpdateProductRequest, DeleteProductResponse

product_router = APIRouter(prefix="/product", tags=["product"])


async def _create_product(body: ProductRequest, db: AsyncSession) -> Optional[Product]:
    async with db as session:
        async with session.begin():
            product_dal = ProductDAL(session)
            category = await CategoryDAL(session).get_category_by_id(category_id=body.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Категория с id "{body.category_id}" не найдена'
                )
            product = await product_dal.create_product(
                name=body.name,
                description=body.description,
                price=body.price,
                stock_quantity=body.stock_quantity,
                category=category,
                manufacturer=body.manufacturer
            )
            return product


async def _get_product_by_id(product_id: UUID, db: AsyncSession) -> Optional[Product]:
    async with db as session:
        async with session.begin():
            product_dal = ProductDAL(session)
            product = await product_dal.get_product_by_id(product_id=product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Продукт c id: {product_id} не найдены"
                )
            return product


async def _get_products(page: int, limit: int, db: AsyncSession) -> Sequence[Row[tuple[Product]]]:
    if limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="За раз можно получить не более 100 продуктов"
        )
    async with db as session:
        async with session.begin():
            product_dal = ProductDAL(session)
            products = await product_dal.get_products(page, limit)
            if not products:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Продукты не найдены"
                )
            return products


async def _delete_product(product_id: UUID, db: AsyncSession) -> UUID:
    async with db as session:
        async with session.begin():
            product_dal = ProductDAL(session)
            product_id = await product_dal.delete_product(product_id=product_id)
            if not product_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Продукт с product_id: {product_id} не найден"
                )
            return product_id


async def _update_product(product_id: UUID, body: UpdateProductRequest, db: AsyncSession) -> Product:
    body = body.model_dump(exclude_none=True)
    if not body:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Должен быть указан хотя бы один параметр для информации об обновлении продукта")
    async with db as session:
        async with session.begin():
            product_dal = ProductDAL(db_session=db)
            product = await product_dal.update_product(product_id=product_id, **body)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Продукт с product_id: {product_id} не найден"
                )
            return product


@product_router.post("/", description="Создать продукт", response_model=ProductResponse)
async def create_product(body: ProductRequest, db: AsyncSession = Depends(get_db)):
    try:
        product = await _create_product(body, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return ProductResponse.model_validate(product)


@product_router.get("/get-products/", description="Получить все продукты", response_model=List[ProductResponse])
async def get_products(page: int = 1, limit: int = 10, db: AsyncSession = Depends(get_db)):
    try:
        products = await _get_products(page, limit, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return [ProductResponse.model_validate(product[0]) for product in products]


@product_router.get("/get-product-by-id/", description="Получить продукт по id", response_model=ProductResponse)
async def get_product_by_id(product_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        product = await _get_product_by_id(product_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return ProductResponse.model_validate(product)


@product_router.delete("/", description="Удалить продукт", response_model=DeleteProductResponse)
async def delete_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        product_id = await _delete_product(product_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return DeleteProductResponse(product_id=product_id)


@product_router.put("/", description="Обновить продукт", response_model=ProductResponse)
async def update_product(product_id: UUID, body: UpdateProductRequest, db: AsyncSession = Depends(get_db)):
    try:
        product = await _update_product(product_id, body, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return ProductResponse.model_validate(product)
