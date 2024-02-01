from typing import Optional, List

from pydantic import BaseModel, Field
from uuid import UUID
from app.schemas.tuned_model import TunedModel


class AttributeRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=20)
    description: str = Field(..., min_length=10, max_length=400)


class AttributeResponse(TunedModel):
    attribute_id: UUID
    name: str
    description: str


class UpdateAttributeRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=20)
    description: Optional[str] = Field(None, min_length=10, max_length=400)


class DeleteAttributeResponse(TunedModel):
    attribute_id: UUID
