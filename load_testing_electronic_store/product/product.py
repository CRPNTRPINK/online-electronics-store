from locust import HttpUser, task, between
from faker import Faker
import random
from utils.generate_string import generate_string
from collections import deque
from PIL import Image
import io


class Product(HttpUser):
    wait_time = between(1, 2)
    category_id = deque()
    attribute_id = deque()
    category_attribute_id = deque()
    product_id = deque()

    def on_start(self):
        self.faker = Faker()

    @task
    def create_category(self):
        # Генерация названия категории
        name = generate_string(3, 20, self.faker)
        # Генерация описания
        description = generate_string(10, 400, self.faker)

        data = {
            "name": name,
            "description": description
        }

        response = self.client.post("/product-management/category/", json=data)
        if response.status_code == 200:
            if len(self.category_id) == 100:
                self.category_id.popleft()
            self.category_id.append(response.json()['category_id'])

    @task
    def create_attribute(self):

        # Генерация названия атрибута
        name = generate_string(3, 20, self.faker)

        # Генерация описания атрибута
        description = generate_string(10, 400, self.faker)

        data = {
            "name": name,
            "description": description
        }

        response = self.client.post("/product-management/attribute/", json=data)
        if response.status_code == 200:
            if len(self.attribute_id) == 100:
                self.attribute_id.popleft()
            self.attribute_id.append(response.json()['attribute_id'])

    @task
    def create_category_attribute(self):
        if self.category_id and self.attribute_id:
            category_id = random.choice(self.category_id)
            attribute_id = random.choice(self.attribute_id)
            data = {
                "category_id": category_id,
                "attribute_id": attribute_id
            }

            response = self.client.post("/product-management/category-attribute/", json=data)
            if response.status_code == 200:
                if len(self.category_attribute_id) == 100:
                    self.category_attribute_id.popleft()
                self.category_attribute_id.append(response.json()['category_attribute_id'])

    @task
    def create_product(self):
        if self.category_id:
            name = generate_string(3, 100, self.faker)
            description = generate_string(5, 250, self.faker
                                          )
            price = round(random.uniform(0.01, 1000.0), 2)
            stock_quantity = 1_000_000
            category_id = random.choice(self.category_id)
            manufacturer = generate_string(3, 15, self.faker)
            data = {
                "name": name,
                "description": description,
                "price": price,
                "stock_quantity": stock_quantity,
                "category_id": category_id,
                "manufacturer": manufacturer
            }

            response = self.client.post("/product-management/product/", json=data)
            if response.status_code == 200:
                if len(self.product_id) == 100:
                    self.product_id.popleft()
                self.product_id.append(response.json()['product_id'])

    @task
    def upload_image(self):
        # Генерация простого изображения
        if self.product_id:
            image = Image.new('RGB', (100, 100), color='red')
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            # Случайный UUID для product_id
            product_id = random.choice(self.product_id)
            description = generate_string(5, 50, self.faker)

            files = {
                'file': ('test_image.jpg', img_byte_arr, 'image/jpeg'),
                'description': (None, description),
                'product_id': (None, product_id)
            }

            self.client.post("/product-management/image/upload-image/", files=files)


if __name__ == "__main__":
    import os

    os.system("locust -f product.py --modern-ui --host=http://localhost:8082")
