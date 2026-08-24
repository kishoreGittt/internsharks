from datetime import datetime


def create_refresh_session_document(
    user_id: str,
    jti_hash: str,
    expires_at: datetime
):

    return {
        "user_id": user_id,
        "jti_hash": jti_hash,
        "expires_at": expires_at,
        "created_at": datetime.utcnow(),
        "revoked": False
    }