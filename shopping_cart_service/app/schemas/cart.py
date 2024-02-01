from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.schemas.tunned_model import TunedModel


class DeleteCartByIdRequest(BaseModel):
    cart_id: UUID


class DeleteCartByIdResponse(TunedModel):
    cart_id: UUID


class CartResponse(TunedModel):
    cart_id: UUID
    user_id: UUID
    created_date: datetime
    last_updated: Optional[datetime]
