from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.tunned_model import TunedModel


class OrderDetailsBase(TunedModel):
    order_id: UUID
    product_id: UUID
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)


class CreateOrderDetails(OrderDetailsBase):
    pass
