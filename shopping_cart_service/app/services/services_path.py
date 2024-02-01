from enum import Enum
from app.settings import IS_LOCAL


class Paths(Enum):
    auth = f"http://{'localhost' if IS_LOCAL else 'authentication'}:8081/auth"
    product_management = f"http://{'localhost' if IS_LOCAL else 'product-management'}:8082/product-management"


class Product(Enum):
    get_product = f'{Paths.product_management.value}/product/get-product-by-id/'
    update_product = f'{Paths.product_management.value}/product/'


class Auth(Enum):
    get_user = f'{Paths.auth.value}/user/'
