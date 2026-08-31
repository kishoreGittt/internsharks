from fastapi import (
    APIRouter,
    File,
    Form,
    UploadFile
)

from app.models.summarizer import (
    DocumentSummarizeResponse
)

from app.services.document_service import (
    summarize_document
)


router = APIRouter(
    prefix="/ai",
    tags=["Document Summarization"]
)


@router.post(
    "/summarize-document",
    response_model=DocumentSummarizeResponse
)
async def summarize_uploaded_document(
    file: UploadFile = File(...),
    summary_type: str = Form(...)
):

    content = await file.read()

    result = await summarize_document(
        filename=file.filename,
        content=content,
        summary_type=summary_type
    )

    return {
        "success": True,
        "status_code": 200,
        "data": result
    }