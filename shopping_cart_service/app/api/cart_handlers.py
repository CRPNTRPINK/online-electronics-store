from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dals.cart import CartDAL
from app.db.models import Cart
from app.services.auth import get_user_by_id


async def create_cart(user_id: UUID, db: AsyncSession) -> Cart:
    await get_user_by_id(user_id=user_id)
    cart_dal = CartDAL(db_session=db)
    new_cart = await cart_dal.create_cart(user_id=user_id)
    return new_cart


async def get_cart_by_user_id(user_id: UUID, db: AsyncSession) -> Optional[Cart]:
    cart_dal = CartDAL(db_session=db)
    cart = await cart_dal.get_cart_by_user_id(user_id=user_id)
    if cart:
        return cart


async def delete_cart_by_id(cart_id: UUID, db: AsyncSession) -> Optional[UUID]:
    cart_dal = CartDAL(db_session=db)
    cart = await cart_dal.delete_cart_by_id(cart_id=cart_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Корзина с id: {cart_id} не найдена"
        )
    return cart
