from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.review import ReviewRequest, ReviewResponse, GetReviewResponse
from app.schemas.user_info import ShowUser
from app.db.session import get_db
from app.db.dals.review import ReviewDAL
from app.db.dals.product import ProductDAL
from app.db.models import Review
from sqlalchemy.engine.row import Row, Sequence

review_router = APIRouter(prefix="/review", tags=["review"])


async def _create_review(body: ReviewRequest, user: ShowUser, db: AsyncSession) -> Review:
    async with db as session:
        async with session.begin():
            product = await ProductDAL(db_session=db).get_product_by_id(product_id=body.product_id)
            review_dal = ReviewDAL(db_session=db)
            review = await review_dal.create_review(
                product=product,
                user_id=user.user_id,
                review_text=body.review_text,
                rating=body.rating
            )
            return review


async def _get_reviews_by_user_id(user_id: UUID,
                                  db: AsyncSession = Depends(get_db)) -> Optional[Sequence[Row[tuple[Review]]]]:
    async with db as session:
        async with session.begin():
            review_dal = ReviewDAL(db_session=db)
            reviews = await review_dal.get_reviews_by_user_id(user_id=user_id)
            if not reviews:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"У пользователя с user_id: {user_id} нет комментариев"
                )
            return reviews


async def _get_reviews_by_product_id(product_id: UUID,
                                     db: AsyncSession = Depends(get_db)) -> Optional[Sequence[Row[tuple[Review]]]]:
    async with db as session:
        async with session.begin():
            review_dal = ReviewDAL(db_session=db)
            reviews = await review_dal.get_reviews_by_product_id(product_id=product_id)
            if not reviews:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"У продукта с product_id: {product_id} нет комментариев"
                )
            return reviews


async def _get_review_by_id(review_id: UUID,
                            db: AsyncSession = Depends(get_db)) -> Optional[Review]:
    async with db as session:
        async with session.begin():
            review_dal = ReviewDAL(db_session=db)
            review = await review_dal.get_review_by_id(review_id=review_id)
            if not review:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Комментарий с review_id: {review_id} не найден"
                )
            return review


async def _delete_review(review_id: UUID, db: AsyncSession = Depends(get_db)) -> Optional[UUID]:
    async with db as session:
        async with session.begin():
            review_dal = ReviewDAL(db_session=db)
            review = await review_dal.delete_review(review_id=review_id)
            if not review:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Комментарий с review_id: {review_id} не найден"
                )
            return review


@review_router.post("/", description="Создать комментарий", response_model=ReviewResponse)
async def create_review(body: ReviewRequest,
                        user_id: Annotated[str, Cookie(...)],
                        db: AsyncSession = Depends(get_db)):
    try:
        review = await _create_review(
            body,
            ShowUser(user_id=user_id),
            db
        )
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return ReviewResponse.model_validate(review)


@review_router.get("/get-review-by-user-id",
                   description="Получить комментарии по id пользователя",
                   response_model=List[GetReviewResponse])
async def get_reviews_by_user_id(user_id: UUID,
                                 db: AsyncSession = Depends(get_db)):
    try:
        reviews = await _get_reviews_by_user_id(user_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return [GetReviewResponse.model_validate(review[0]) for review in reviews]


@review_router.get("/get-review-by-product-id",
                   description="Получить комментарии по id продукта",
                   response_model=List[GetReviewResponse])
async def get_reviews_by_product_id(product_id: UUID,
                                    db: AsyncSession = Depends(get_db)):
    try:
        reviews = await _get_reviews_by_product_id(product_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return [GetReviewResponse.model_validate(review[0]) for review in reviews]


@review_router.get("/get-review-by-id",
                   description="Получить комментарий по id",
                   response_model=GetReviewResponse)
async def get_reviews_by_id(review_id: UUID,
                            db: AsyncSession = Depends(get_db)):
    try:
        review = await _get_review_by_id(review_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return GetReviewResponse.model_validate(review)


@review_router.delete("/",
                      description="Удалить комментарий",
                      response_model=ReviewResponse)
async def delete_review(review_id: UUID,
                        db: AsyncSession = Depends(get_db)):
    try:
        review_id = await _delete_review(review_id, db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return ReviewResponse(review_id=review_id)
