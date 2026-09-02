from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status
)

from app.models.rag import (
    AskRequest
)

from app.services.rag_service import (
    RAGService
)


router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


rag_service = RAGService()


@router.post(
    "/documents",
    status_code=status.HTTP_201_CREATED
)
async def upload_document(
    file: UploadFile = File(...)
):

    try:

        file_bytes = await file.read()


        result = (
            rag_service.process_document(

                file_name=file.filename,

                file_bytes=file_bytes
            )
        )


        return {

            "success": True,

            "status_code": 201,

            "data": result

        }


    except ValueError as exc:

        raise HTTPException(

            status_code=400,

            detail=str(exc)

        )


    except RuntimeError as exc:

        raise HTTPException(

            status_code=502,

            detail=str(exc)

        )


    except Exception:

        raise HTTPException(

            status_code=500,

            detail="Document processing failed"

        )


@router.post("/ask")
async def ask_question(
    request: AskRequest
):

    try:

        answer = (
            rag_service.ask_question(

                document_id=
                    request.document_id,

                question=
                    request.question
            )
        )


        return {

            "success": True,

            "status_code": 200,

            "data": {

                "document_id":
                    request.document_id,

                "question":
                    request.question,

                "answer":
                    answer

            }

        }


    except ValueError as exc:

        raise HTTPException(

            status_code=400,

            detail=str(exc)

        )


    except RuntimeError as exc:

        raise HTTPException(

            status_code=502,

            detail=str(exc)

        )


    except Exception:

        raise HTTPException(

            status_code=500,

            detail="Question processing failed"

        )


@router.get(
    "/documents/{document_id}"
)
async def get_document(
    document_id: str
):

    document = (
        rag_service.get_document(
            document_id
        )
    )


    if document is None:

        raise HTTPException(

            status_code=404,

            detail="Document not found"

        )


    return {

        "success": True,

        "status_code": 200,

        "data": document

    }