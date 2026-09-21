import time

from app.config import settings

from app.storage.vector_store import (
    add_documents,
    search
)


# =========================================================
# INDEX DOCUMENT
# =========================================================

async def index_document(
    owner_id: str,
    document_id: str,
    chunks: list[str]
):

    start_time = time.perf_counter()

    count = add_documents(
        owner_id=owner_id,
        document_id=document_id,
        chunks=chunks
    )

    elapsed_ms = (
        time.perf_counter()
        - start_time
    ) * 1000

    print(
        f"Indexed {count} chunks "
        f"in {elapsed_ms:.2f} ms"
    )

    return {
        "document_id": document_id,
        "chunks_indexed": count
    }


# =========================================================
# RETRIEVE
# =========================================================

async def retrieve(
    owner_id: str,
    query: str,
    document_ids: list[str]
):

    retrieval_start = time.perf_counter()

    results = search(
        owner_id=owner_id,
        query=query,
        document_ids=document_ids,
        top_k=settings.TOP_K
    )

    retrieval_time = (
        time.perf_counter()
        - retrieval_start
    )

    return {
        "results": results,

        "embedding_time_ms": round(
            retrieval_time * 1000,
            2
        ),

        "retrieval_time_ms": round(
            retrieval_time * 1000,
            2
        )
    }


# =========================================================
# BUILD CONTEXT
# =========================================================

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

Similarity Score: {item.get("score")}

Content:
{item.get("text", "")}
"""
        )

    return "\n".join(
        context_parts
    )