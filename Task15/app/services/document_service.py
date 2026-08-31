from fastapi import HTTPException

from app.config import MAX_FILE_SIZE

from app.services.summarizer_service import (
    summarize_text
)

from app.utils.file_parser import (
    extract_text_from_file
)


ALLOWED_EXTENSIONS = {
    ".txt",
    ".pdf"
}


def get_extension(filename: str) -> str:

    filename = filename.lower()

    if "." not in filename:

        return ""

    return "." + filename.rsplit(".", 1)[1]


async def summarize_document(
    filename: str,
    content: bytes,
    summary_type: str
):

    # Missing filename
    if not filename:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "FILE_REQUIRED",
                "message": "File is required"
            }
        )

    extension = get_extension(filename)

    # Unsupported file type
    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=415,
            detail={
                "error": "UNSUPPORTED_FILE_TYPE",
                "message": (
                    "Only .txt and .pdf files are allowed"
                )
            }
        )

    # Empty file
    if not content:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "EMPTY_FILE",
                "message": "Uploaded file is empty"
            }
        )

    # File size
    if len(content) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=413,
            detail={
                "error": "FILE_TOO_LARGE",
                "message": "File size exceeds the 5 MB limit"
            }
        )

    # Summary type
    if summary_type not in {
        "brief",
        "detailed",
        "bullet_points"
    }:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_SUMMARY_TYPE",
                "message": (
                    "Summary type must be "
                    "brief, detailed, or bullet_points"
                )
            }
        )

    # Extract text
    try:

        extracted_text = extract_text_from_file(
            filename,
            content
        )

    except ValueError as error:

        raise HTTPException(
            status_code=422,
            detail={
                "error": "DOCUMENT_EXTRACTION_FAILED",
                "message": str(error)
            }
        )

    except Exception:

        raise HTTPException(
            status_code=422,
            detail={
                "error": "DOCUMENT_EXTRACTION_FAILED",
                "message": (
                    "Unable to extract text from document"
                )
            }
        )

    # No extractable text
    if not extracted_text or not extracted_text.strip():

        raise HTTPException(
            status_code=422,
            detail={
                "error": "NO_EXTRACTABLE_TEXT",
                "message": (
                    "No extractable text found in the document"
                )
            }
        )

    # Reuse existing summarization logic
    ai_result = await summarize_text(
        extracted_text,
        summary_type
    )

    return {
        "file_name": filename,
        "summary_type": summary_type,
        "summary": ai_result.summary,
        "main_topic": ai_result.main_topic,
        "keywords": ai_result.keywords
    }