from datetime import datetime, timezone
from typing import Optional

from app.storage.mongodb import (
    documents_collection,
    chunks_collection,
)


def utc_now():
    return datetime.now(timezone.utc)


async def create_document(document: dict):
    """
    Create a document record.

    Both user_id and owner_id are supported for compatibility.
    """

    # Make sure both ownership fields exist.
    if document.get("user_id") and not document.get("owner_id"):
        document["owner_id"] = document["user_id"]

    if document.get("owner_id") and not document.get("user_id"):
        document["user_id"] = document["owner_id"]

    document["created_at"] = utc_now()
    document["updated_at"] = utc_now()

    await documents_collection.insert_one(document)

    document.pop("_id", None)

    return document


async def get_document(
    user_id: str,
    document_id: str
) -> Optional[dict]:
    """
    Get a document belonging to the authenticated user.

    Supports both old documents using owner_id and new documents
    using user_id.
    """

    document = await documents_collection.find_one(
        {
            "document_id": document_id,
            "$or": [
                {"user_id": user_id},
                {"owner_id": user_id},
            ],
        },
        {
            "_id": 0
        }
    )

    return document


async def find_by_hash(
    user_id: str,
    content_hash: str
) -> Optional[dict]:
    """
    Find an existing document belonging to the user.
    """

    return await documents_collection.find_one(
        {
            "content_hash": content_hash,
            "$or": [
                {"user_id": user_id},
                {"owner_id": user_id},
            ],
        },
        {
            "_id": 0
        }
    )


async def update_document_status(
    user_id: str,
    document_id: str,
    status: str,
    error: Optional[str] = None
):
    """
    Update document processing status while respecting ownership.
    """

    query = {
        "document_id": document_id,
        "$or": [
            {"user_id": user_id},
            {"owner_id": user_id},
        ],
    }

    update_data = {
        "status": status,
        "updated_at": utc_now(),
    }

    if error:
        update_data["error"] = error

    update = {
        "$set": update_data
    }

    if not error:
        update["$unset"] = {
            "error": ""
        }

    await documents_collection.update_one(
        query,
        update
    )


async def insert_chunks(
    user_id: str,
    document_id: str,
    chunks: list[dict]
):
    """
    Store processed document chunks.
    """

    if not chunks:
        return

    records = []

    for chunk in chunks:

        records.append(
            {
                "user_id": user_id,

                "owner_id": user_id,

                "document_id": document_id,

                "chunk_id": chunk["chunk_id"],

                "text": chunk["text"],

                "chunk_index": chunk.get(
                    "chunk_index",
                    0
                ),

                "created_at": utc_now(),
            }
        )

    await chunks_collection.insert_many(
        records
    )


async def get_chunks(
    user_id: str,
    document_id: str
):
    """
    Get chunks belonging to the authenticated user.
    """

    cursor = chunks_collection.find(
        {
            "document_id": document_id,
            "$or": [
                {"user_id": user_id},
                {"owner_id": user_id},
            ],
        },
        {
            "_id": 0
        }
    ).sort(
        "chunk_index",
        1
    )

    return await cursor.to_list(
        length=None
    )


async def delete_document_chunks(
    user_id: str,
    document_id: str
):
    """
    Delete chunks belonging to the authenticated user.
    """

    await chunks_collection.delete_many(
        {
            "document_id": document_id,
            "$or": [
                {"user_id": user_id},
                {"owner_id": user_id},
            ],
        }
    )