from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/red-team",
    tags=["Red Team"]
)


@router.get("/status")
async def red_team_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Check whether Red Team testing is enabled.
    """

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "red_team": "enabled",
            "user_id": current_user.get("user_id")
        }
    }