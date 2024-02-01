from app.schemas.tuned_model import TunedModel
from app.schemas.product import ProductResponse
from app.schemas.attribute import AttributeResponse
from pydantic import BaseModel
from uuid import UUID
from pydantic import Field


class ProductAttributeRequest(BaseModel):
    product_id: UUID
    attribute_id: UUID
    value: str = Field(..., min_length=1, max_length=100, description="Значение параметра")


class ProductAttributeResponse(TunedModel):
    product_attribute_id: UUID
    product: ProductResponse
    attribute: AttributeResponse
    value: str


class DeleteProductAttributeResponse(TunedModel):
    product_attribute_id: UUID
