from motor.motor_asyncio import AsyncIOMotorClient

from app.config import (
    MONGODB_DATABASE,
    MONGODB_URI,
)


client = None
db = None
traces_collection = None
spans_collection = None


async def connect_to_mongodb():
    global client
    global db
    global traces_collection
    global spans_collection

    if not MONGODB_URI:
        raise RuntimeError(
            "MONGODB_URI is not configured."
        )

    client = AsyncIOMotorClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
    )

    await client.admin.command(
        "ping"
    )

    db = client[MONGODB_DATABASE]

    traces_collection = db["traces"]
    spans_collection = db["spans"]

    await traces_collection.create_index(
        "trace_id",
        unique=True,
    )

    await traces_collection.create_index(
        "status"
    )

    await traces_collection.create_index(
        "model"
    )

    await traces_collection.create_index(
        "prompt_version"
    )

    await traces_collection.create_index(
        "start_time"
    )

    await traces_collection.create_index(
        "total_duration_ms"
    )

    await spans_collection.create_index(
        "trace_id"
    )


async def close_mongodb():
    global client

    if client is not None:
        client.close()
        client = None


def get_traces_collection():
    if traces_collection is None:
        raise RuntimeError(
            "MongoDB is not connected."
        )

    return traces_collection


def get_spans_collection():
    if spans_collection is None:
        raise RuntimeError(
            "MongoDB is not connected."
        )

    return spans_collection