from datetime import datetime, timezone
from typing import Optional

from app.storage.mongodb import (
    documents_collection,
    chunks_collection,
)


def utc_now():
    return datetime.now(timezone.utc)


async def create_document(document: dict):
    document["created_at"] = utc_now()
    document["updated_at"] = utc_now()

    await documents_collection.insert_one(document)

    return document


async def get_document(
    user_id: str,
    document_id: str
) -> Optional[dict]:

    return await documents_collection.find_one(
        {
            "user_id": user_id,
            "document_id": document_id,
        },
        {"_id": 0}
    )


async def find_by_hash(
    user_id: str,
    content_hash: str
) -> Optional[dict]:

    return await documents_collection.find_one(
        {
            "user_id": user_id,
            "content_hash": content_hash,
        },
        {"_id": 0}
    )


async def update_document_status(
    user_id: str,
    document_id: str,
    status: str,
    error: Optional[str] = None
):

    update = {
        "$set": {
            "status": status,
            "updated_at": utc_now(),
        }
    }

    if error:
        update["$set"]["error"] = error
    else:
        update["$unset"] = {"error": ""}

    await documents_collection.update_one(
        {
            "user_id": user_id,
            "document_id": document_id,
        },
        update
    )


async def insert_chunks(
    user_id: str,
    document_id: str,
    chunks: list[dict]
):

    if not chunks:
        return

    records = []

    for chunk in chunks:
        records.append(
            {
                "user_id": user_id,
                "document_id": document_id,
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "chunk_index": chunk.get("chunk_index", 0),
                "created_at": utc_now(),
            }
        )

    await chunks_collection.insert_many(records)


async def get_chunks(
    user_id: str,
    document_id: str
):

    cursor = chunks_collection.find(
        {
            "user_id": user_id,
            "document_id": document_id,
        },
        {"_id": 0}
    ).sort("chunk_index", 1)

    return await cursor.to_list(length=None)


async def delete_document_chunks(
    user_id: str,
    document_id: str
):

    await chunks_collection.delete_many(
        {
            "user_id": user_id,
            "document_id": document_id,
        }
    )