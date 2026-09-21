from pathlib import Path
import uuid

from fastapi import UploadFile, HTTPException

from app.config import settings

from app.storage.repositories.job_repository import create_job

from app.storage.mongodb import documents_collection


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt"
}


async def create_document(
    file: UploadFile,
    owner_id: str
):
    """
    Upload and register a document.

    The authenticated user's ID is stored as both:
    - user_id
    - owner_id

    user_id is used by document/RAG access control.
    owner_id is kept for compatibility with the job worker.
    """

    # ---------------------------------------------------------
    # Validate filename
    # ---------------------------------------------------------
    filename = file.filename or ""

    if not filename:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "error": "INVALID_FILENAME",
                "message": "A document filename is required."
            }
        )

    # ---------------------------------------------------------
    # Validate extension
    # ---------------------------------------------------------
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "error": "INVALID_DOCUMENT_TYPE",
                "message": "Only PDF and TXT files are supported."
            }
        )

    # ---------------------------------------------------------
    # Read uploaded file
    # ---------------------------------------------------------
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "error": "EMPTY_DOCUMENT",
                "message": "The uploaded document is empty."
            }
        )

    # ---------------------------------------------------------
    # Check file size
    # ---------------------------------------------------------
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail={
                "success": False,
                "status_code": 413,
                "error": "FILE_TOO_LARGE",
                "message": "File exceeds the maximum allowed size."
            }
        )

    # ---------------------------------------------------------
    # Generate IDs
    # ---------------------------------------------------------
    document_id = str(uuid.uuid4())

    job_id = str(uuid.uuid4())

    # ---------------------------------------------------------
    # Create upload directory
    # ---------------------------------------------------------
    upload_directory = Path(
        settings.UPLOAD_DIR
    )

    upload_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    # ---------------------------------------------------------
    # Save file
    # ---------------------------------------------------------
    file_path = (
        upload_directory
        / f"{document_id}{extension}"
    )

    file_path.write_bytes(content)

    # ---------------------------------------------------------
    # Create document record
    #
    # IMPORTANT:
    # Store user_id because get_document() searches using
    # user_id + document_id.
    #
    # owner_id is also stored for worker compatibility.
    # ---------------------------------------------------------
    document = {
        "document_id": document_id,

        "user_id": owner_id,

        "owner_id": owner_id,

        "filename": filename,

        "path": str(file_path),

        "status": "queued",

        "progress": 0,

        "error": None
    }

    # ---------------------------------------------------------
    # Save document to MongoDB
    # ---------------------------------------------------------
    await documents_collection.insert_one(
        document
    )

    # ---------------------------------------------------------
    # Create asynchronous processing job
    # ---------------------------------------------------------
    await create_job(
        job_id=job_id,
        document_id=document_id,
        owner_id=owner_id
    )

    return document_id, job_id


def extract_text(
    file_path: str
):
    """
    Extract text from TXT or PDF document.
    """

    path = Path(file_path)

    # ---------------------------------------------------------
    # TXT
    # ---------------------------------------------------------
    if path.suffix.lower() == ".txt":

        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    # ---------------------------------------------------------
    # PDF
    # ---------------------------------------------------------
    if path.suffix.lower() == ".pdf":

        from pypdf import PdfReader

        reader = PdfReader(
            str(path)
        )

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)

    raise ValueError(
        "Unsupported document format"
    )


def chunk_text(
    text: str
):
    """
    Split extracted document text into overlapping chunks.
    """

    text = " ".join(
        text.split()
    )

    chunks = []

    start = 0

    while start < len(text):

        end = min(
            start + settings.CHUNK_SIZE,
            len(text)
        )

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        if end >= len(text):
            break

        start = (
            end
            - settings.CHUNK_OVERLAP
        )

    return chunks