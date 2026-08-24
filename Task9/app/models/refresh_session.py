from datetime import datetime
from typing import Optional


def create_refresh_session_document(
    user_id: str,
    jti_hash: str,
    expires_at: datetime
) -> dict:

    return {
        "user_id": user_id,
        "jti_hash": jti_hash,
        "expires_at": expires_at,
        "revoked": False,
        "created_at": datetime.utcnow()
    }