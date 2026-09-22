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

from app.storage.mongodb import (
    documents_collection
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
            owner_id=current_user[
                "user_id"
            ]
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


@router.get(
    "/documents"
)
async def get_documents(

    current_user: dict = Depends(
        get_current_user
    )

):

    owner_id = current_user[
        "user_id"
    ]

    cursor = documents_collection.find(
        {
            "owner_id": owner_id
        },
        {
            "_id": 0
        }
    )

    documents = []

    async for document in cursor:

        documents.append(
            document
        )

    return {

        "success": True,

        "status_code": 200,

        "data": documents
    }


@router.get(
    "/documents/{document_id}"
)
async def get_document_details(

    document_id: str,

    current_user: dict = Depends(
        get_current_user
    )

):

    owner_id = current_user[
        "user_id"
    ]

    document = await documents_collection.find_one(
        {
            "document_id":
                document_id,

            "owner_id":
                owner_id
        },
        {
            "_id": 0
        }
    )

    if not document:

        return {
            "success": False,
            "status_code": 404,
            "error": "DOCUMENT_NOT_FOUND",
            "message": (
                "Document not found."
            )
        }

    return {

        "success": True,

        "status_code": 200,

        "data": document
    }