import asyncio

from app.storage.repositories.job_repository import (
    claim_next_job,
    update_job
)

from app.storage.mongodb import documents_collection

from app.services.document_service import (
    extract_text,
    chunk_text
)

from app.services.rag_service import (
    index_document
)


async def process_job(job: dict):
    """
    Process one document ingestion job.

    Flow:
        queued
          ↓
        processing
          ↓
        extract text
          ↓
        chunk text
          ↓
        create embeddings / index
          ↓
        completed
    """

    job_id = job["job_id"]

    document_id = job["document_id"]

    owner_id = (
        job.get("owner_id")
        or job.get("user_id")
    )

    try:

        print("\n==========================================")
        print("        DOCUMENT JOB STARTED")
        print("==========================================")
        print(f"Job ID       : {job_id}")
        print(f"Document ID  : {document_id}")
        print(f"Owner ID     : {owner_id}")
        print("==========================================\n")

        # -----------------------------------------------------
        # Find document
        # -----------------------------------------------------

        document = await documents_collection.find_one(
            {
                "document_id": document_id,
                "$or": [
                    {"user_id": owner_id},
                    {"owner_id": owner_id}
                ]
            }
        )

        if not document:

            await update_job(
                job_id=job_id,
                status="failed",
                progress=100,
                error="Document not found."
            )

            print(
                f"Document not found: {document_id}"
            )

            return

        # -----------------------------------------------------
        # PROCESSING
        # -----------------------------------------------------

        await update_job(
            job_id=job_id,
            status="processing",
            progress=10
        )

        await documents_collection.update_one(
            {
                "document_id": document_id,
                "$or": [
                    {"user_id": owner_id},
                    {"owner_id": owner_id}
                ]
            },
            {
                "$set": {
                    "status": "processing",
                    "progress": 10
                }
            }
        )

        print("Status: processing")

        # -----------------------------------------------------
        # EXTRACT TEXT
        # -----------------------------------------------------

        print("Extracting document text...")

        text = extract_text(
            document["path"]
        )

        if not text or not text.strip():

            raise ValueError(
                "No readable text was extracted from the document."
            )

        await update_job(
            job_id=job_id,
            status="processing",
            progress=35
        )

        print(
            f"Extracted characters: {len(text)}"
        )

        # -----------------------------------------------------
        # CHUNK TEXT
        # -----------------------------------------------------

        print("Creating document chunks...")

        chunks = chunk_text(
            text
        )

        if not chunks:

            raise ValueError(
                "Document produced no chunks."
            )

        await update_job(
            job_id=job_id,
            status="processing",
            progress=55
        )

        print(
            f"Created chunks: {len(chunks)}"
        )

        # -----------------------------------------------------
        # EMBEDDING + VECTOR INDEX
        # -----------------------------------------------------

        print("Creating embeddings and indexing document...")

        await index_document(
            owner_id=owner_id,
            document_id=document_id,
            chunks=chunks
        )

        await update_job(
            job_id=job_id,
            status="processing",
            progress=85
        )

        # -----------------------------------------------------
        # DOCUMENT READY
        # -----------------------------------------------------

        await documents_collection.update_one(
            {
                "document_id": document_id,
                "$or": [
                    {"user_id": owner_id},
                    {"owner_id": owner_id}
                ]
            },
            {
                "$set": {
                    "status": "ready",
                    "progress": 100
                }
            }
        )

        # IMPORTANT:
        # Job status should be completed.
        # Document status should be ready.
        await update_job(
            job_id=job_id,
            status="completed",
            progress=100
        )

        print("\n==========================================")
        print("        DOCUMENT JOB COMPLETED")
        print("==========================================")
        print(f"Job ID       : {job_id}")
        print(f"Document ID  : {document_id}")
        print("Status       : completed")
        print("Document     : ready")
        print("==========================================\n")

    except Exception as error:

        print("\n==========================================")
        print("        DOCUMENT JOB FAILED")
        print("==========================================")
        print(f"Job ID       : {job_id}")
        print(f"Document ID  : {document_id}")
        print(f"Error type   : {type(error).__name__}")
        print(f"Error        : {error}")
        print("==========================================\n")

        await update_job(
            job_id=job_id,
            status="failed",
            progress=100,
            error=str(error)
        )

        await documents_collection.update_one(
            {
                "document_id": document_id,
                "$or": [
                    {"user_id": owner_id},
                    {"owner_id": owner_id}
                ]
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
    """
    Continuously check MongoDB for queued jobs.
    """

    while True:

        try:

            job = await claim_next_job()

            if job:

                print(
                    f"Processing job: {job['job_id']}"
                )

                await process_job(
                    job
                )

            else:

                await asyncio.sleep(2)

        except asyncio.CancelledError:

            print(
                "Document worker stopped."
            )

            raise

        except Exception as error:

            print(
                f"Worker loop error: {error}"
            )

            await asyncio.sleep(2)


if __name__ == "__main__":

    asyncio.run(
        worker_loop()
    )