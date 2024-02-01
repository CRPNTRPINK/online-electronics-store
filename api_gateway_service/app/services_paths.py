from enum import Enum
from app.settings import IS_LOCAL


class Paths(Enum):
    auth = f"http://{'localhost' if IS_LOCAL else 'authentication'}:8081/auth"
    product_management = f"http://{'localhost' if IS_LOCAL else 'product-management'}:8082/product-management"
    shopping_cart = f"http://{'localhost' if IS_LOCAL else 'shopping-cart'}:8083/shopping_cart"
