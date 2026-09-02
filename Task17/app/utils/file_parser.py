from io import BytesIO

from PyPDF2 import PdfReader


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt"
}


def extract_text(
    file_bytes: bytes,
    file_name: str
) -> str:

    extension = (
        "."
        + file_name.lower().split(".")[-1]
    )

    # TXT
    if extension == ".txt":

        return file_bytes.decode(
            "utf-8",
            errors="ignore"
        )


    # PDF
    if extension == ".pdf":

        pdf_file = BytesIO(file_bytes)

        reader = PdfReader(pdf_file)

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:

                pages.append(text)


        return "\n".join(pages)


    raise ValueError(
        "Only PDF and TXT files are supported"
    )


def clean_text(text: str) -> str:

    lines = []

    for line in text.splitlines():

        cleaned = " ".join(
            line.split()
        )

        if cleaned:

            lines.append(cleaned)


    return "\n".join(lines)