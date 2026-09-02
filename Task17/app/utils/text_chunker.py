from app.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
):

    if not text:

        return []


    if chunk_overlap >= chunk_size:

        raise ValueError(
            "Chunk overlap must be smaller than chunk size"
        )


    chunks = []

    start = 0

    text_length = len(text)


    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()


        if chunk:

            chunks.append(chunk)


        if end >= text_length:

            break


        start = end - chunk_overlap


    return chunks