from pydantic import BaseModel, Field
from uuid import UUID
from app.schemas.category import CategoryResponse
from app.schemas.attribute import AttributeResponse
from app.schemas.tuned_model import TunedModel
from typing import Optional, List


class ProductRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=5, max_length=250)
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., gt=0)
    category_id: UUID
    manufacturer: str = Field(..., min_length=3, max_length=15)


class UpdateProductRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=5, max_length=250)
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, gt=0)
    category_id: Optional[UUID] = None
    manufacturer: Optional[str] = Field(None, min_length=3, max_length=15)


class DeleteProductResponse(TunedModel):
    product_id: UUID


class ProductImageResponse(TunedModel):
    image_id: UUID
    image_name: str
    description: str


class ProductAttributeResponse(TunedModel):
    product_attribute_id: UUID
    attribute: AttributeResponse
    value: str


class ProductResponse(TunedModel):
    product_id: UUID
    name: str
    description: str
    price: float
    stock_quantity: int
    category: Optional[CategoryResponse] = None
    product_images: Optional[List[ProductImageResponse]] = None
    product_attribute_values: Optional[List[ProductAttributeResponse]] = None
    # reviews = Optional[List[ProductImageResponse]] = None
    manufacturer: str
