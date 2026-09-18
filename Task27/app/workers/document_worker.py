import asyncio

from app.storage.repositories.job_repository import (
    get_next_job,
    update_job
)

from app.storage.mongodb import (
    documents_collection
)

from app.services.document_service import (
    extract_text,
    chunk_text
)

from app.services.rag_service import (
    index_document
)


async def process_job(job):

    job_id = job["job_id"]

    document_id = job["document_id"]

    owner_id = job["owner_id"]

    try:

        document = await documents_collection.find_one(
            {
                "document_id": document_id,
                "owner_id": owner_id
            }
        )

        if not document:

            await update_job(
                job_id,
                {
                    "status": "failed",
                    "progress": 100,
                    "error": "Document not found."
                }
            )

            return

        await update_job(
            job_id,
            {
                "status": "processing",
                "progress": 10
            }
        )

        await documents_collection.update_one(

            {
                "document_id": document_id,
                "owner_id": owner_id
            },

            {
                "$set": {
                    "status": "processing",
                    "progress": 10
                }
            }
        )

        # -------------------------
        # Extract
        # -------------------------

        text = extract_text(
            document["path"]
        )

        await update_job(
            job_id,
            {
                "progress": 35
            }
        )

        # -------------------------
        # Chunk
        # -------------------------

        chunks = chunk_text(
            text
        )

        await update_job(
            job_id,
            {
                "progress": 55
            }
        )

        # -------------------------
        # Embedding + Vector Store
        # -------------------------

        await index_document(
            owner_id=owner_id,
            document_id=document_id,
            chunks=chunks
        )

        await update_job(
            job_id,
            {
                "progress": 85
            }
        )

        # -------------------------
        # READY
        # -------------------------

        await update_job(
            job_id,
            {
                "status": "ready",
                "progress": 100
            }
        )

        await documents_collection.update_one(

            {
                "document_id": document_id,
                "owner_id": owner_id
            },

            {
                "$set": {
                    "status": "ready",
                    "progress": 100
                }
            }
        )

    except Exception as error:

        await update_job(
            job_id,
            {
                "status": "failed",
                "progress": 100,
                "error": str(error)
            }
        )

        await documents_collection.update_one(

            {
                "document_id": document_id,
                "owner_id": owner_id
            },

            {
                "$set": {
                    "status": "failed",
                    "progress": 100,
                    "error": str(error)
                }
            }
        )


async def worker_loop():

    print(
        "Task 27 document worker started..."
    )

    while True:

        job = await get_next_job()

        if job:

            print(
                f"Processing job: {job['job_id']}"
            )

            await process_job(job)

        else:

            await asyncio.sleep(2)


if __name__ == "__main__":

    asyncio.run(
        worker_loop()
    )