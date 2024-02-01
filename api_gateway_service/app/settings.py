import os

from dotenv import load_dotenv

load_dotenv()

IS_LOCAL = os.getenv("IS_LOCAL", "true").lower() == "true"

TOKEN_VERIFY_URL = f"http://{'localhost' if IS_LOCAL else 'authentication'}:8081/auth/user/token_verify/"

SERVICES_TOKEN = "f574657465d6ffd86bc4a0b991ad6e125e1b47b3271d15a5ab312cf803d84117"
