from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, and_
from sqlalchemy.orm import selectinload
from app.db.models import CartItem
from sqlalchemy.engine.row import Row, Sequence
from uuid import UUID


class CartItemDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_cart_item(self, cart_id: UUID, product_id: UUID,price: float) -> CartItem:
        new_cart_item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            price=price
        )
        self.db_session.add(new_cart_item)
        await self.db_session.flush()
        return new_cart_item

    async def get_cart_items(self) -> Optional[Sequence[Row[tuple[CartItem]]]]:
        query = select(CartItem)
        res = await self.db_session.execute(query)
        cart_items = res.fetchall()
        if cart_items:
            return cart_items

    async def get_cart_item_by_cart_id(self, cart_id: UUID, product_id: UUID) -> Optional[CartItem]:
        query = (select(CartItem).
                 where(and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id)))
        res = await self.db_session.execute(query)
        cart_item = res.fetchone()
        if cart_item:
            return cart_item[0]

    async def get_cart_item_by_id(self, cart_item_id: UUID) -> Optional[CartItem]:
        query = (select(CartItem).
                 where(CartItem.cart_item_id == cart_item_id))
        res = await self.db_session.execute(query)
        cart_item = res.fetchone()
        if cart_item:
            return cart_item[0]

    async def delete_cart_item_by_id(self, cart_item_id: UUID) -> Optional[UUID]:
        query = (delete(CartItem).
                 where(CartItem.cart_item_id == cart_item_id).
                 returning(CartItem.cart_item_id))
        res = await self.db_session.execute(query)
        cart_item = res.fetchone()
        if cart_item:
            return cart_item[0]
