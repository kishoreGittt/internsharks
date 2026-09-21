from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException
)

from app.auth.dependencies import (
    get_current_user
)

from app.services.document_service import (
    create_document
)

from app.storage.repositories.document_repository import (
    get_document
)


router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"]
)


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

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


# ============================================================
# GET DOCUMENT
# ============================================================

@router.get(
    "/documents/{document_id}"
)
async def get_document_details(

    document_id: str,

    current_user: dict = Depends(
        get_current_user
    )
):

    user_id = current_user["user_id"]

    document = await get_document(
        user_id=user_id,
        document_id=document_id
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "status_code": 404,
                "error": "DOCUMENT_NOT_FOUND",
                "message": "Document not found."
            }
        )

    return {

        "success": True,

        "status_code": 200,

        "data": {

            "document_id":
                document.get("document_id"),

            "filename":
                document.get("filename"),

            "status":
                document.get("status"),

            "progress":
                document.get("progress", 0),

            "error":
                document.get("error"),

            "created_at":
                document.get("created_at"),

            "updated_at":
                document.get("updated_at")
        }
    }