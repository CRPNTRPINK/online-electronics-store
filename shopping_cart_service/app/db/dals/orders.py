from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.engine.row import Row, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Orders


class OrdersDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_order(self, user_id: UUID, total_amount: float, status: str, shipping_address: str) -> Orders:
        new_order = Orders(
            user_id=user_id,
            total_amount=total_amount,
            status=status,
            shipping_address=shipping_address
        )
        self.db_session.add(new_order)
        await self.db_session.flush()
        return new_order

    async def get_orders(self) -> Optional[Sequence[Row[tuple[Orders]]]]:
        query = select(Orders)
        res = await self.db_session.execute(query)
        orders = res.fetchall()
        if orders:
            return orders

    async def get_orders_by_user_id(self, user_id: UUID) -> Optional[Sequence[Row[tuple[Orders]]]]:
        query = (select(Orders).
                 where(Orders.user_id == user_id))
        res = await self.db_session.execute(query)
        orders = res.fetchall()
        if orders:
            return orders

    async def get_order_by_id(self, order_id: UUID) -> Optional[Orders]:
        query = (select(Orders).
                 where(Orders.id == order_id))
        res = await self.db_session.execute(query)
        order = res.fetchone()
        if order:
            return order[0]

    async def update_order(self, order_id: UUID, **kwargs) -> Optional[Orders]:
        query = (update(Orders).
                 where(Orders.order_id == order_id).
                 values(kwargs).
                 returning(Orders))
        res = await self.db_session.execute(query)
        order = res.fetchone()
        if order:
            return order[0]
