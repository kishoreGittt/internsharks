import time

from app.config import settings

from app.storage.vector_store import (
    add_documents,
    search
)


async def index_document(
    owner_id: str,
    document_id: str,
    chunks: list[str]
):

    if not chunks:

        raise ValueError(
            "No document chunks were created."
        )

    count = add_documents(
        owner_id=owner_id,
        document_id=document_id,
        chunks=chunks
    )

    return {
        "document_id": document_id,
        "chunks_indexed": count
    }


async def retrieve(
    owner_id: str,
    query: str,
    document_ids: list[str]
):

    if not document_ids:

        return {
            "results": [],
            "embedding_time_ms": 0,
            "retrieval_time_ms": 0
        }

    embedding_start = time.perf_counter()

    results = search(
        owner_id=owner_id,
        query=query,
        document_ids=document_ids,
        top_k=settings.TOP_K
    )

    elapsed = (
        time.perf_counter()
        - embedding_start
    ) * 1000

    return {
        "results": results,
        "embedding_time_ms": round(
            elapsed,
            2
        ),
        "retrieval_time_ms": 0
    }


def build_context(
    results: list[dict]
):

    if not results:
        return ""

    context_parts = []

    for item in results:

        context_parts.append(
            f"""
Document ID: {item.get("document_id")}

Chunk ID: {item.get("chunk_id")}

Content:
{item.get("text", "")}
"""
        )

    return "\n".join(
        context_parts
    )