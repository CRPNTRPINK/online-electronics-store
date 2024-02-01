from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dals.cart_item import CartItemDAL
from app.db.models import CartItem
from app.db.session import get_db
from app.schemas.cart_item import (AddCartItemRequest,
                                   AddCartItemResponse,
                                   ReduceCartItemRequest,
                                   GetCartItemResponse)
from app.services.product_management import get_product_by_id
from app.api.cart_handlers import (get_cart_by_user_id,
                                   create_cart,
                                   delete_cart_by_id)

cart_item_router = APIRouter(prefix="/cart-item", tags=['cart-item'])


async def _add_product(body: AddCartItemRequest,
                       user_id: UUID,
                       db: AsyncSession) -> JSONResponse:
    async with db as session:
        async with session.begin():
            cart = await get_cart_by_user_id(user_id=user_id, db=db)
            if not cart:
                cart = await create_cart(user_id=user_id, db=db)

            cart_item = await _get_cart_item_by_cart_id(
                cart_id=cart.cart_id,
                product_id=body.product_id,
                db=db
            )
            if not cart_item:
                cart_item = await _create_cart_item(
                    cart_id=cart.cart_id,
                    product_id=body.product_id,
                    db=db
                )
            else:
                cart_item = await _increase_quantity(cart_item=cart_item)
            return cart_item


async def _get_cart_item_by_cart_id(cart_id: UUID, product_id: UUID, db: AsyncSession) -> Optional[CartItem]:
    cart_item_dal = CartItemDAL(db_session=db)
    cart_item = await cart_item_dal.get_cart_item_by_cart_id(
        cart_id=cart_id,
        product_id=product_id
    )
    if cart_item:
        return cart_item


async def _create_cart_item(cart_id: UUID, product_id: UUID, db: AsyncSession) -> JSONResponse:
    cart_item_dal = CartItemDAL(db_session=db)
    product = await get_product_by_id(product_id)
    new_cart_item = await cart_item_dal.create_cart_item(
        cart_id=cart_id,
        product_id=product_id,
        price=product['price']
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=AddCartItemResponse.model_validate(new_cart_item).model_dump(mode='json')
    )


async def _increase_quantity(cart_item: CartItem) -> JSONResponse:
    product = await get_product_by_id(cart_item.product_id)
    if product['stock_quantity'] == cart_item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Продукт недоступен. В наличии всего {product['stock_quantity']} штук")
    cart_item.quantity += 1
    cart_item.price += product['price']
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=AddCartItemResponse.model_validate(cart_item).model_dump(mode='json')
    )


async def _remove_product(body: ReduceCartItemRequest,
                          user_id: UUID,
                          db: AsyncSession):
    async with db as session:
        async with session.begin():
            cart = await get_cart_by_user_id(user_id=user_id, db=db)
            if not cart:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Отсутствует корзина'
                )

            cart_item = await _get_cart_item_by_cart_id(
                cart_id=cart.cart_id,
                product_id=body.product_id,
                db=db
            )
            if not cart_item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Продукт c id: {body.product_id} отсутствует в корзине c id: {cart.cart_id}'
                )
            await reduce_quantity(cart_item=cart_item, db=db)
            await session.refresh(cart)
            if not cart.items:
                await delete_cart_by_id(cart_id=cart.cart_id, db=db)


async def delete_cart_item_by_id(cart_item_id: UUID, db: AsyncSession) -> UUID:
    cart_item_dal = CartItemDAL(db_session=db)
    cart_item = await cart_item_dal.delete_cart_item_by_id(cart_item_id=cart_item_id)
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Элемент корзины с id: {cart_item_id} не найден"
        )
    return cart_item


async def reduce_quantity(cart_item: CartItem, db: AsyncSession):
    product = await get_product_by_id(cart_item.product_id)
    cart_item.quantity -= 1
    cart_item.price -= product['price']
    if cart_item.quantity != 0:
        return

    await delete_cart_item_by_id(cart_item_id=cart_item.cart_item_id, db=db)


async def _get_cart_item_by_id(cart_item_id: UUID, db: AsyncSession) -> Optional[CartItem]:
    async with db as session:
        async with session.begin():
            cart_item_dal = CartItemDAL(db_session=db)
            cart_item = await cart_item_dal.get_cart_item_by_id(cart_item_id=cart_item_id)
            if not cart_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Элемент корзины с id: {cart_item_id} не существует"
                )
            return cart_item


@cart_item_router.post('/', description='Создать элемент корзины', response_model=AddCartItemResponse)
async def add_cart_item(body: AddCartItemRequest, user_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        cart_item = await _add_product(body=body, user_id=user_id, db=db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return cart_item


@cart_item_router.patch('/', description='Удалить элемент корзины')
async def reduce_cart_item(body: ReduceCartItemRequest, user_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        await _remove_product(body=body, user_id=user_id, db=db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Operation completed successfully"})


@cart_item_router.get('/', description='Получит элемент корзины по id', response_model=GetCartItemResponse)
async def get_cart_item_by_id(cart_item_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        cart_item = await _get_cart_item_by_id(cart_item_id=cart_item_id, db=db)
    except HTTPException as er:
        raise er
    except Exception as er:
        raise HTTPException(status_code=500, detail=er.args[-1])
    return GetCartItemResponse.model_validate(cart_item)
