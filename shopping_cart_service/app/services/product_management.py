import json
from uuid import UUID

from fastapi import HTTPException, status

from app.services.services_path import Product
from app.state import get_http_client


async def get_product_by_id(product_id: UUID):
    params = {'product_id': str(product_id)}
    headers = {
        'accept': 'application/json'
    }
    async with get_http_client().get(Product.get_product.value, params=params, headers=headers) as response:
        if response.status != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status, detail=await response.json())
        return await response.json()


async def update_product(product_id, product_data):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {'product_id': str(product_id)}

    async with get_http_client().put(Product.update_product.value,
                               params=params,
                               headers=headers,
                               data=json.dumps(product_data)) as response:
        if response.status != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status, detail=await response.json())
        return await response.json()


async def update_product_stock_quantity(product_id: UUID, stock_quantity: int) -> dict:
    product_data = {
        "name": None,
        "description": None,
        "price": None,
        "stock_quantity": stock_quantity,
        "category_id": None,
        "manufacturer": None
    }
    return await update_product(product_id, product_data)
