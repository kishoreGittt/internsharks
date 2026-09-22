from pathlib import Path
import uuid

from fastapi import (
    UploadFile,
    HTTPException
)

from app.config import settings

from app.storage.repositories.job_repository import (
    create_job
)

from app.storage.mongodb import (
    documents_collection
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt"
}


async def create_document(
    file: UploadFile,
    owner_id: str
):

    filename = (
        file.filename
        or ""
    ).strip()

    if not filename:

        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "error": "EMPTY_FILENAME",
                "message": "Filename is required."
            }
        )

    extension = (
        Path(filename)
        .suffix
        .lower()
    )

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "error": "INVALID_DOCUMENT_TYPE",
                "message": (
                    "Only PDF and TXT files are supported."
                )
            }
        )

    content = await file.read()

    if not content:

        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "error": "EMPTY_FILE",
                "message": "Uploaded file is empty."
            }
        )

    if len(content) > settings.MAX_FILE_SIZE:

        raise HTTPException(
            status_code=413,
            detail={
                "success": False,
                "status_code": 413,
                "error": "FILE_TOO_LARGE",
                "message": (
                    "File exceeds the maximum allowed size."
                )
            }
        )

    document_id = str(
        uuid.uuid4()
    )

    job_id = str(
        uuid.uuid4()
    )

    upload_directory = Path(
        settings.UPLOAD_DIR
    )

    upload_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = (
        upload_directory
        / f"{document_id}{extension}"
    )

    file_path.write_bytes(
        content
    )

    document = {

        "document_id":
            document_id,

        "owner_id":
            owner_id,

        "filename":
            filename,

        "path":
            str(file_path),

        "status":
            "queued",

        "progress":
            0,

        "error":
            None
    }

    await documents_collection.insert_one(
        document
    )

    await create_job(
        job_id=job_id,
        document_id=document_id,
        owner_id=owner_id
    )

    return (
        document_id,
        job_id
    )


def extract_text(
    file_path: str
):

    path = Path(
        file_path
    )

    if path.suffix.lower() == ".txt":

        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

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

        return "\n".join(
            pages
        )

    raise ValueError(
        "Unsupported document format"
    )


def chunk_text(
    text: str
):

    text = " ".join(
        text.split()
    )

    if not text:

        return []

    chunks = []

    start = 0

    while start < len(text):

        end = min(
            start + settings.CHUNK_SIZE,
            len(text)
        )

        chunk = text[
            start:end
        ]

        if chunk.strip():

            chunks.append(
                chunk
            )

        if end >= len(text):

            break

        next_start = (
            end
            - settings.CHUNK_OVERLAP
        )

        if next_start <= start:

            next_start = end

        start = next_start

    return chunks