from locust import HttpUser, task, between, events
import requests
from random import choice
from collections import deque, Counter
from utils.generate_string import generate_string
from faker import Faker

users_ids = []
products_ids = []


def get_users():
    url = 'http://localhost:8081/auth/user/'
    response = requests.get(url, headers={'accept': 'application/json'})
    if response.status_code == 200:
        users = response.json()
        for user in users:
            if len(users_ids) == 100:
                break
            users_ids.append(user['user_id'])


def get_products():
    url = 'http://localhost:8082/product-management/product/get-products/?page=1&limit=100'
    response = requests.get(url, headers={'accept': 'application/json'})
    if response.status_code == 200:
        products = response.json()
        for products in products:
            products_ids.append(products['product_id'])


@events.test_start.add_listener
def on_test_start_listener(environment, **kwargs):
    get_users()
    get_products()


class ShoppingCartUser(HttpUser):
    wait_time = between(1, 5)
    users_ids_counter = Counter()
    prepared_users_ids = deque()

    def on_start(self):
        self.faker = Faker()

    @task(2)
    def add_to_cart(self):
        if products_ids and users_ids:
            data = {"product_id": choice(products_ids)}
            user_id = choice(users_ids)
            response = self.client.post(
                f"/shopping_cart/cart-item/?user_id={user_id}",
                json=data,
                name='/shopping_cart/cart-item/?user_id=[user_id]'
            )
            if response.status_code in (200, 201):
                self.users_ids_counter[user_id] += 1
                if self.users_ids_counter[user_id] >= 5:
                    self.prepared_users_ids.append(user_id)
                    del self.users_ids_counter[user_id]

    @task(1)
    def add_to_orders(self):
        if self.prepared_users_ids:
            user_id = self.prepared_users_ids.popleft()
            address = generate_string(3, 30, self.faker)
            data = {
                "shipping_address": address,
                "user_id": user_id
            }
            with self.client.post('/shopping_cart/orders/', json=data, catch_response=True) as response:
                # Дополнительная логика для проверки содержимого ответа
                if response.status_code == 201:
                    response.success()
                else:
                    # Отметить запрос как неуспешный, если статус код не 200
                    response.failure(f"Status code: {response.status_code} "
                                     f"{response.text}")


if __name__ == "__main__":
    import os

    os.system("locust -f shopping_cart.py --modern-ui --host=http://localhost:8083")
