from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.tunned_model import TunedModel


class CartItemBase(TunedModel):
    cart_id: UUID
    product_id: UUID


class CartItemResponseBase(CartItemBase):
    cart_item_id: UUID
    quantity: int
    price: float


class AddCartItemRequest(BaseModel):
    product_id: UUID


class ReduceCartItemRequest(AddCartItemRequest):
    pass


class AddCartItemResponse(CartItemResponseBase):
    pass


class RemoveCartItemResponse(CartItemResponseBase):
    pass


class GetCartItemResponse(CartItemResponseBase):
    pass
