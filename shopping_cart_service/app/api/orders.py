import asyncio
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.cart_handlers import get_cart_by_user_id
from app.db.dals.order_details import OrderDetailsDAL
from app.db.dals.orders import OrdersDAL
from app.db.models import CartItem
from app.db.models import Orders
from app.db.session import get_db
from app.schemas.order_details import CreateOrderDetails
from app.schemas.orders import (OrderStatus,
                                TotalAmount,
                                CreateOrderRequest,
                                CreateOrderResponse,
                                UpdateOrderResponse)
from app.schemas.user import UserStatus
from app.services.auth import get_user_by_id
from app.services.product_management import update_product_stock_quantity, get_product_by_id

orders_router = APIRouter(prefix='/orders', tags=['orders'])


async def calculate_total_amount(items: List[CartItem]) -> TotalAmount:
    total_amount = 0
    for item in items:
        total_amount += item.price
    return TotalAmount(total_amount=total_amount)


async def create_orders_details(order_id: UUID, items: List[CartItem], db: AsyncSession):
    orders_details = []
    for item in items:
        orders_details.append(CreateOrderDetails(
            order_id=order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        ))

    order_details_dal = OrderDetailsDAL(db_session=db)
    await order_details_dal.create_order_details(orders_details=orders_details)


async def reduce_product_count(items: List[CartItem]):
    updates = []
    for item in items:
        product = await get_product_by_id(item.product_id)
        if product['stock_quantity'] < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"На складе нет продукта {product['name']} в количестве {item.quantity}"
            )
        c_quantity = product['stock_quantity'] - item.quantity
        updates.append(update_product_stock_quantity(
            product_id=item.product_id,
            stock_quantity=c_quantity
        ))
    return await asyncio.gather(*updates)


async def _create_order(body: CreateOrderRequest, db: AsyncSession) -> Orders:
    async with db as session:
        async with session.begin():
            await get_user_by_id(user_id=body.user_id)
            orders_dal = OrdersDAL(db_session=db)
            cart = await get_cart_by_user_id(user_id=body.user_id, db=db)
            if not cart:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Корзина пользователя с user_id: {body.user_id} не найдена"
                )
            total_amount = await calculate_total_amount(items=cart.items)
            order = await orders_dal.create_order(
                user_id=body.user_id,
                total_amount=total_amount.total_amount,
                status=OrderStatus.NEW.value,
                shipping_address=body.shipping_address
            )

            await create_orders_details(
                order_id=order.order_id,
                items=cart.items,
                db=db
            )
            await reduce_product_count(items=cart.items)
            return order


async def _update_order_status(order_id: UUID, user_role: int, order_status: str, db: AsyncSession) -> Orders:
    async with db as session:
        async with session.begin():
            if user_role != UserStatus.SUPER.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"У вас нет прав, чтобы изменить заказ"
                )
            orders_dal = OrdersDAL(db_session=db)
            order = await orders_dal.update_order(order_id=order_id, status=order_status)
            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Заказ с id: {order_id} не найден"
                )
            return order


@orders_router.post('/', description="Создать заказ",
                    response_model=CreateOrderResponse,
                    status_code=status.HTTP_201_CREATED)
async def create_order(body: CreateOrderRequest, db: AsyncSession = Depends(get_db)):
    try:
        order = await _create_order(body, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return CreateOrderResponse.model_validate(order)


@orders_router.put('/update-status', description="Обновить статус", response_model=UpdateOrderResponse)
async def update_order(order_id: UUID, order_status: OrderStatus, db: AsyncSession = Depends(get_db)):
    try:
        order = await _update_order_status(
            order_id=order_id,
            user_role=1,
            order_status=order_status,
            db=db
        )
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return CreateOrderResponse.model_validate(order)
