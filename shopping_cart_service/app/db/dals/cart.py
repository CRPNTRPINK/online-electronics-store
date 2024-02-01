from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.engine.row import Row, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Cart


class CartDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_cart(self, user_id: UUID) -> Cart:
        new_cart = Cart(user_id=user_id)
        self.db_session.add(new_cart)
        await self.db_session.flush()
        return new_cart

    async def get_carts(self) -> Optional[Sequence[Row[tuple[Cart]]]]:
        query = (select(Cart).
                 options(selectinload(Cart.items)))
        res = await self.db_session.execute(query)
        carts = res.fetchall()
        if carts:
            return carts

    async def get_cart_by_user_id(self, user_id: UUID) -> Optional[Cart]:
        query = (select(Cart).
                 where(Cart.user_id == user_id).
                 options(selectinload(Cart.items)))
        res = await self.db_session.execute(query)
        cart = res.fetchone()
        if cart:
            return cart[0]

    async def get_cart_by_id(self, cart_id: UUID) -> Optional[Cart]:
        query = (select(Cart).
                 where(Cart.id == cart_id).
                 options(selectinload(Cart.items)))
        res = await self.db_session.execute(query)
        cart = res.fetchone()
        if cart:
            return cart[0]

    async def delete_cart_by_id(self, cart_id: UUID) -> Optional[UUID]:
        query = (delete(Cart).
                 where(Cart.cart_id == cart_id).
                 returning(Cart.cart_id))

        res = await self.db_session.execute(query)
        cart_id = res.fetchone()
        if cart_id:
            return cart_id[0]
