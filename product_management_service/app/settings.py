import os

from dotenv import load_dotenv

load_dotenv()

PRODUCT_IMAGE_PATH = "images/product"

DEV = os.getenv("DEV", "true").lower() == "true"

IS_LOCAL = os.getenv("IS_LOCAL", "true").lower() == "true"

REAL_DATABASE_URL = os.getenv(
    "REAL_DATABASE_URL",
    f"postgresql+asyncpg://postgres:postgres@{'localhost' if IS_LOCAL else 'db'}:5432/electronic_store",
)

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    f"postgresql+asyncpg://postgres:postgres@{'localhost' if IS_LOCAL else 'db'}:5432/electronic_store_test",
)
SERVICES_TOKEN = "f574657465d6ffd86bc4a0b991ad6e125e1b47b3271d15a5ab312cf803d84117"
