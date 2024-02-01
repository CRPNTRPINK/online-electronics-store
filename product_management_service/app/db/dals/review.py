from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.engine.row import Row, Sequence

from app.db.models import Review, Product


class ReviewDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_review(self, product: Product, user_id: UUID, review_text: str, rating: int) -> Review:
        new_review = Review(
            product=product,
            user_id=user_id,
            review_text=review_text,
            rating=rating
        )
        self.db_session.add(new_review)
        await self.db_session.flush()
        return new_review

    async def get_reviews_by_user_id(self, user_id: UUID) -> Optional[Sequence[Row[tuple[Review]]]]:
        query = (select(Review).
                 where(Review.user_id == user_id))
        res = await self.db_session.execute(query)
        reviews = res.fetchall()
        if reviews:
            return reviews

    async def get_reviews_by_product_id(self, product_id: UUID) -> Optional[Sequence[Row[tuple[Review]]]]:
        query = (select(Review).
                 where(Review.product_id == product_id))
        res = await self.db_session.execute(query)
        reviews = res.fetchall()
        if reviews:
            return reviews

    async def get_review_by_id(self, review_id: UUID) -> Optional[Review]:
        query = (select(Review).
                 where(Review.review_id == review_id))
        res = await self.db_session.execute(query)
        review = res.fetchone()
        if review:
            return review[0]

    async def delete_review(self, review_id: UUID) -> Optional[UUID]:
        query = (delete(Review).
                 where(Review.review_id == review_id).
                 returning(Review.review_id))
        res = await self.db_session.execute(query)
        deleted_review_id = res.fetchone()
        if deleted_review_id:
            return deleted_review_id[0]
