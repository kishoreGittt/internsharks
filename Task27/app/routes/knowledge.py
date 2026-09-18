from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile
)

from app.auth.dependencies import (
    get_current_user
)

from app.services.document_service import (
    create_document
)


router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"]
)


@router.post(
    "/documents",
    status_code=202
)
async def upload_document(

    file: UploadFile = File(...),

    current_user: dict = Depends(
        get_current_user
    )
):

    document_id, job_id = (
        await create_document(
            file=file,
            owner_id=current_user["user_id"]
        )
    )

    return {

        "success": True,

        "status_code": 202,

        "document_id":
            document_id,

        "job_id":
            job_id,

        "status":
            "queued"
    }