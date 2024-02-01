from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.category import CategoryRequest, CategoryResponse, UpdateCategoryRequest, DeleteCategoryResponse
from app.db.session import get_db
from app.db.dals.category import CategoryDAL
from app.db.models import Category
from sqlalchemy.engine.row import Row

category_router = APIRouter(prefix="/category", tags=["category"])


async def _create_category(body: CategoryRequest, db: AsyncSession):
    async with db as session:
        async with session.begin():
            category_dal = CategoryDAL(session)
            if await category_dal.category_already_exists(body.name):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'Категория с именем "{body.name}" уже существует'
                )
            category = await category_dal.create_category(
                name=body.name,
                description=body.description
            )
            return category


async def _get_category_by_id(category_id: UUID, db: AsyncSession) -> Optional[Category]:
    async with db as session:
        async with session.begin():
            category_dal = CategoryDAL(db_session=db)
            category = await category_dal.get_category_by_id(category_id=category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Категория с category_id: {category_id} не найдена"
                )
            return category


async def _get_categories(db: AsyncSession) -> Optional[List[Row[Category]]]:
    async with db as session:
        async with session.begin():
            category_dal = CategoryDAL(db_session=db)
            categories = await category_dal.get_categories()
            if not categories:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Категорий нет")
            return categories


async def _delete_category(category_id: UUID, db: AsyncSession) -> Optional[UUID]:
    async with db as session:
        async with session.begin():
            category_dal = CategoryDAL(db_session=db)
            deleted_category_id = await category_dal.delete_category(category_id=category_id)
            if not deleted_category_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Категория с category_id: {category_id} не найдена"
                )
            return deleted_category_id


async def _update_category(category_id: UUID,
                           body: UpdateCategoryRequest,
                           db: AsyncSession) -> Optional[CategoryResponse]:
    body = body.model_dump(exclude_none=True)
    if not body:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Должен быть указан хотя бы один параметр для информации об обновлении категории")
    async with db as session:
        async with session.begin():
            category_dal = CategoryDAL(db_session=db)
            category = await category_dal.update_category(category_id=category_id, **body)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Категория с category_id: {category_id} не найдена"
                )
            return category


@category_router.post("/", description="Создать категорию", response_model=CategoryResponse)
async def create_category(body: CategoryRequest, db: AsyncSession = Depends(get_db)):
    try:
        category = await _create_category(body, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])

    return CategoryResponse.model_validate(category)


@category_router.get("/get-categories/", description="Получить все категории", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    try:
        categories = await _get_categories(db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return [CategoryResponse.model_validate(category[0]) for category in categories]


@category_router.get("/get-category-by-id/", description="Получить категорию по id", response_model=CategoryResponse)
async def get_category_by_id(category_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        category = await _get_category_by_id(category_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return CategoryResponse.model_validate(category)


@category_router.delete("/", description="Удалить категорию", response_model=DeleteCategoryResponse)
async def delete_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        category_id = await _delete_category(category_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return DeleteCategoryResponse(category_id=category_id)


@category_router.put("/", description="Обновить категорию", response_model=CategoryResponse)
async def update_category(category_id: UUID, body: UpdateCategoryRequest, db: AsyncSession = Depends(get_db)):
    try:
        category = await _update_category(category_id, body, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return CategoryResponse.model_validate(category)
