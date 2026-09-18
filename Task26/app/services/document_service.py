from pathlib import Path

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader


ALLOWED_EXTENSIONS = {".txt", ".pdf"}


class DocumentService:
    def __init__(self, max_file_size: int) -> None:
        self.max_file_size = max_file_size

    def validate_filename(self, filename: str) -> Path:
        path = Path(filename)

        if not path.name:
            raise HTTPException(
                status_code=400,
                detail="Invalid file name",
            )

        extension = path.suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Only .txt and .pdf files are supported",
            )

        return path

    async def save_upload(
        self,
        upload_file: UploadFile,
        destination: Path,
    ) -> int:
        total_size = 0

        with destination.open("wb") as output:
            while True:
                chunk = await upload_file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > self.max_file_size:
                    output.close()

                    if destination.exists():
                        destination.unlink()

                    raise HTTPException(
                        status_code=413,
                        detail="File size exceeds the maximum limit",
                    )

                output.write(chunk)

        return total_size

    def extract_text(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError("Document file not found")

        extension = path.suffix.lower()

        if extension == ".txt":
            text = path.read_text(
                encoding="utf-8",
                errors="replace",
            )

        elif extension == ".pdf":
            reader = PdfReader(str(path))

            pages = []

            for page in reader.pages:
                pages.append(page.extract_text() or "")

            text = "\n".join(pages)

        else:
            raise ValueError("Unsupported document type")

        text = text.strip()

        if not text:
            raise ValueError(
                "Could not extract readable text from the document"
            )

        return text