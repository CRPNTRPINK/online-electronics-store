# Используем официальный образ Python
FROM python:3.9.6

# Устанавливаем рабочую директорию внутри контейнера
ENV SERVICE_NAME "/product_management_service"
WORKDIR ${SERVICE_NAME}

# Сначала копируем только файл requirements.txt, чтобы использовать кэш Docker
COPY requirements.txt requirements.txt

# устанавливаем зависимости
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:${SERVICE_NAME}"

# Теперь копируем остальные файлы приложения
COPY ./app app
COPY ./migrations migrations
COPY alembic.ini alembic.ini
COPY logging_config.yaml logging_config.yaml