from locust import HttpUser, task, between, constant
from faker import Faker
from random import choice
from collections import deque


class UserBehavior(HttpUser):
    wait_time = constant(1)
    email_passwd = deque()
    token = deque()

    def on_start(self):
        """ Вызывается при создании каждого пользователя """
        self.faker = Faker()

    @task(1)
    def create_user(self):
        # Генерация уникальных данных пользователя
        name = self.faker.first_name()
        surname = self.faker.last_name()
        email = self.faker.email()
        password = self.faker.password()

        # Создание тела запроса
        data = {
            "name": name,
            "surname": surname,
            "email": email,
            "password": password,
            "password_confirm": password
        }

        # Отправка POST-запроса
        response = self.client.post("/auth/user/", json=data, headers={
            'accept': 'application/json',
            'Content-Type': 'application/json'
        })
        if response.status_code == 200:
            if self.email_passwd:
                self.email_passwd.popleft()
            self.email_passwd.append((email, password))

    @task(1)
    def post_token(self):
        if self.email_passwd:
            email, password = self.email_passwd[0]
            data = {
                'grant_type': '',
                'username': email,
                'password': password,
                'scope': '',
                'client_id': '',
                'client_secret': ''
            }
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            response = self.client.post("/auth/user/token", data=data, headers=headers)
            if response.status_code == 201:
                if self.token:
                    self.token.popleft()
                self.token.append(response.cookies.get('token'))

    @task(1)
    def verify_token(self):
        if self.token:
            token = self.token[0]
            headers = {
                'accept': 'application/json',
                'Cookie': f'token={token}'
            }

            self.client.get("/auth/user/token_verify", headers=headers)


if __name__ == "__main__":
    import os

    os.system("locust -f auth.py --modern-ui --host=http://localhost:8081")
