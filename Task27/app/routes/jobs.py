from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.storage.repositories.job_repository import get_job


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.get("/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "status_code": 401,
                "error": "INVALID_USER",
                "message": "User information is missing from token.",
            },
        )

    job = await get_job(
        user_id=user_id,
        job_id=job_id,
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "status_code": 404,
                "error": "JOB_NOT_FOUND",
                "message": "Job not found.",
            },
        )

    return {
        "success": True,
        "status_code": 200,
        "data": job,
    }