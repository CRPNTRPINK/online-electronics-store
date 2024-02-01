from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.engine.row import Row, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.order_details import CreateOrderDetails
from app.db.models import OrderDetails


class OrderDetailsDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_order_details(self, orders_details: List[CreateOrderDetails]):
        models = []
        for order_details in orders_details:
            models.append(OrderDetails(
                order_id=order_details.order_id,
                product_id=order_details.product_id,
                quantity=order_details.quantity,
                price=order_details.price
            ))
        self.db_session.add_all(models)

    async def update_quantity(self, order_details_id: UUID, new_quantity: int) -> OrderDetails.quantity:
        query = (update(OrderDetails).
                 where(OrderDetails.id == order_details_id).
                 values(quantity=new_quantity).
                 returning(OrderDetails.quantity))
        res = await self.db_session.execute(query)
        quantity = res.fetchone()
        return quantity

    async def update_price(self, order_details_id: UUID, new_price: float) -> OrderDetails.price:
        query = (update(OrderDetails).
                 where(OrderDetails.id == order_details_id).
                 values(price=new_price).
                 returning(OrderDetails.price))
        res = await self.db_session.execute(query)
        quantity = res.fetchone()
        return quantity

    async def get_order_details(self) -> Optional[Sequence[Row[tuple[OrderDetails]]]]:
        query = select(OrderDetails)
        res = await self.db_session.execute(query)
        order_details = res.fetchall()
        if order_details:
            return order_details

    async def get_order_details_by_order_id(self, order_id: UUID) -> Optional[OrderDetails]:
        query = (select(OrderDetails).
                 where(OrderDetails.order_id == order_id))
        res = await self.db_session.execute(query)
        order_details = res.fetchone()
        if order_details:
            return order_details[0]

    async def get_order_details_by_id(self, order_details_id: UUID) -> Optional[OrderDetails]:
        query = (select(OrderDetails).
                 where(OrderDetails.id == order_details_id))
        res = await self.db_session.execute(query)
        order_details = res.fetchone()
        if order_details:
            return order_details[0]
