from typing import Optional

from pydantic import BaseModel, Field
from uuid import UUID
from app.schemas.tuned_model import TunedModel


class CategoryRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=20)
    description: str = Field(..., min_length=10, max_length=400)


class CategoryResponse(TunedModel):
    category_id: UUID
    name: str
    description: str


class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=20)
    description: Optional[str] = Field(None, min_length=10, max_length=400)


class DeleteCategoryResponse(TunedModel):
    category_id: UUID
