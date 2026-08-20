import os

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# MongoDB Configuration
# ============================================================

MONGO_URI = os.getenv("MONGO_URI")

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "task7_auth_db"
)


# ============================================================
# JWT Configuration
# ============================================================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

try:
    JWT_EXPIRE_MINUTES = int(
        os.getenv(
            "JWT_EXPIRE_MINUTES",
            "30"
        )
    )
except ValueError:
    raise RuntimeError(
        "JWT_EXPIRE_MINUTES must be a valid integer"
    )


# ============================================================
# Configuration Validation
# ============================================================

if not MONGO_URI:
    raise RuntimeError(
        "MONGO_URI is not configured in .env"
    )


if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is not configured in .env"
    )


if len(JWT_SECRET_KEY) < 32:
    raise RuntimeError(
        "JWT_SECRET_KEY should contain at least 32 characters"
    )


if JWT_EXPIRE_MINUTES <= 0:
    raise RuntimeError(
        "JWT_EXPIRE_MINUTES must be greater than 0"
    )