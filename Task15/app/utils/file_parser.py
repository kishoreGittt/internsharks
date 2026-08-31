from io import BytesIO

from PyPDF2 import PdfReader


def extract_text_from_txt(content: bytes) -> str:

    try:

        return content.decode("utf-8")

    except UnicodeDecodeError:

        raise ValueError(
            "TXT file must be UTF-8 encoded"
        )


def extract_text_from_pdf(content: bytes) -> str:

    try:

        reader = PdfReader(BytesIO(content))

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    except Exception:

        raise ValueError(
            "PDF extraction failed"
        )


def extract_text_from_file(
    filename: str,
    content: bytes
) -> str:

    filename = filename.lower()

    if filename.endswith(".txt"):

        return extract_text_from_txt(content)

    if filename.endswith(".pdf"):

        return extract_text_from_pdf(content)

    raise ValueError(
        "Unsupported file type"
    )