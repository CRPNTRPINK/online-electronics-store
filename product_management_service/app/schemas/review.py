from pydantic import BaseModel, Field
from app.schemas.tuned_model import TunedModel
from uuid import UUID


class ReviewRequest(BaseModel):
    product_id: UUID
    review_text: str = Field(..., min_length=1, max_length=300)
    rating: int = Field(..., gt=1, le=10)


class GetReviewResponse(TunedModel):
    review_id: UUID
    product_id: UUID
    user_id: UUID
    review_text: str
    rating: int


class ReviewResponse(TunedModel):
    review_id: UUID
