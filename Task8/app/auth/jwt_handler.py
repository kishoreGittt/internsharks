from datetime import (
    datetime,
    timedelta,
    timezone
)

from jose import jwt

from app.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


# ============================================================
# CREATE TOKEN
# ============================================================

def create_access_token(
    email: str
):

    expire = (
        datetime.now(timezone.utc)
        +
        timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": email,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


# ============================================================
# DECODE TOKEN
# ============================================================

def decode_access_token(
    token: str
):

    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[
            JWT_ALGORITHM
        ]
    )

    return payload