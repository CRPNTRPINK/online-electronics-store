import os
import shutil
import uuid

from fastapi import UploadFile, HTTPException

from app.settings import PRODUCT_IMAGE_PATH


def save_image(image: UploadFile) -> str:
    filename = f"{uuid.uuid4()}{image.filename[image.filename.rfind('.'):]}"
    with open(f"{PRODUCT_IMAGE_PATH}/{filename}", "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    return filename


def remove_image(image_name: str):
    file_path = f"{PRODUCT_IMAGE_PATH}/{image_name}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
