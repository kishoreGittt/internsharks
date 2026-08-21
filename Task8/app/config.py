import os
from dotenv import load_dotenv


load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "task8_db"
)

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "change-this-secret"
)

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "60"
    )
)

ADMIN_SETUP_KEY = os.getenv(
    "ADMIN_SETUP_KEY",
    "change-admin-setup-key"
)


if not MONGO_URI:
    raise ValueError(
        "MONGO_URI is missing in .env"
    )