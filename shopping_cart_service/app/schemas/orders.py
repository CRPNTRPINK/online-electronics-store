from enum import Enum
from uuid import UUID
from pydantic import BaseModel
from pydantic import Field
from app.schemas.tunned_model import TunedModel


class OrderStatus(str, Enum):
    NEW = 'new'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELED = 'canceled'
    RETURNED = 'returned'


class TotalAmount(BaseModel):
    total_amount: float = Field(..., gt=0)


class UserId(BaseModel):
    user_id: UUID


class ShippingAddress(BaseModel):
    shipping_address: str = Field(..., min_length=5, max_length=30, description="Адрес доставки")


class OrderId(BaseModel):
    order_id: UUID


class Status(BaseModel):
    status: OrderStatus


class CreateOrderRequest(UserId, ShippingAddress):
    pass


class CreateOrderResponse(TunedModel, Status, TotalAmount, ShippingAddress, UserId, OrderId):
    pass


class UpdateOrderResponse(TunedModel, Status, TotalAmount, ShippingAddress, UserId, OrderId):
    pass


class GetOrderResponse(UserId, ShippingAddress, TotalAmount, TunedModel):
    order_id: UUID
