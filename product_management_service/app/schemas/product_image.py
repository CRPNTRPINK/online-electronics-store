from uuid import UUID
from app.schemas.product import ProductResponse
from app.schemas.tuned_model import TunedModel
from pydantic import BaseModel

class ProductImageResponse(TunedModel):
    image_id: UUID
    image_name: str
    description: str
    product: ProductResponse


class DeleteProductImageResponse(BaseModel):
    image_name: str
