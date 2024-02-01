from typing import List, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.engine.row import Row, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dals.cart import CartDAL
from app.db.models import Cart
from app.db.session import get_db
from app.schemas.cart import (CartResponse,
                              DeleteCartByIdResponse)

cart_router = APIRouter(prefix="/cart", tags=['cart'])


async def _get_carts(db: AsyncSession) -> Sequence[Row[tuple[Cart]]]:
    async with db as session:
        async with session.begin():
            cart_dal = CartDAL(db_session=db)
            carts = await cart_dal.get_carts()
            if not carts:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Корзин нет"
                )
            return carts


async def _get_cart_by_user_id(user_id: UUID, db: AsyncSession) -> Cart:
    async with db as session:
        async with session.begin():
            cart_dal = CartDAL(db_session=db)
            cart = await cart_dal.get_cart_by_user_id(user_id=user_id)
            if not cart:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Корзина пользователя с id: {user_id} не найдена"
                )
            return cart


async def _get_cart_by_id(cart_id: UUID, db: AsyncSession) -> Cart:
    async with db as session:
        async with session.begin():
            cart_dal = CartDAL(db_session=db)
            cart = await cart_dal.get_cart_by_id(cart_id=cart_id)
            if not cart:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Корзина с id: {cart_id} не найдена"
                )
            return cart


async def _delete_cart_by_id(cart_id: UUID, db: AsyncSession) -> UUID:
    async with db as session:
        async with session.begin():
            cart_dal = CartDAL(db_session=db)
            cart_id = await cart_dal.delete_cart_by_id(cart_id=cart_id)
            if not cart_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Корзина с id: {cart_id} не найдена"
                )
            return cart_id


@cart_router.get('/', description="получить список корзин", response_model=List[CartResponse])
async def get_carts(db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        carts = await _get_carts(db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return [CartResponse.model_validate(cart[0]) for cart in carts]


@cart_router.get('/get-cart-by-id',
                 description="получить корзину по id пользователя",
                 response_model=CartResponse)
async def get_cart_by_id(cart_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        cart = await _get_cart_by_id(cart_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return CartResponse.model_validate(cart)


@cart_router.get('/get-cart-by-user-id',
                 description="получить по id",
                 response_model=CartResponse)
async def get_cart_by_user_id(user_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        cart = await _get_cart_by_user_id(user_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return CartResponse.model_validate(cart)


@cart_router.delete('/', description="удалить корзину", response_model=DeleteCartByIdResponse)
async def delete_cart_by_id(cart_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        cart_id = await _delete_cart_by_id(cart_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return DeleteCartByIdResponse(cart_id=cart_id)
