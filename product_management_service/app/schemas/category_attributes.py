from pydantic import BaseModel
from uuid import UUID
from app.schemas.category import CategoryResponse
from app.schemas.attribute import AttributeResponse
from app.schemas.tuned_model import TunedModel


class CategoryAttributesRequest(BaseModel):
    category_id: UUID
    attribute_id: UUID


class CategoryAttributesResponse(TunedModel):
    category_attribute_id: UUID
    category: CategoryResponse
    attribute: AttributeResponse


class DeleteCategoryAttributeResponse(TunedModel):
    category_attribute_id: UUID
