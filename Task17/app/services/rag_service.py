import os
import uuid

from app.config import (
    DOCUMENT_DIR,
    MAX_FILE_SIZE,
    TOP_K
)

from app.prompts.rag_prompt import (
    RAG_SYSTEM_PROMPT
)

from app.services.ai_service import (
    AIService
)

from app.services.embedding_service import (
    EmbeddingService
)

from app.storage.vector_store import (
    VectorStore
)

from app.utils.file_parser import (
    ALLOWED_EXTENSIONS,
    clean_text,
    extract_text
)

from app.utils.text_chunker import (
    split_text
)


class RAGService:

    def __init__(self):

        os.makedirs(
            DOCUMENT_DIR,
            exist_ok=True
        )


        self.embedding_service = (
            EmbeddingService()
        )

        self.vector_store = (
            VectorStore()
        )

        self.ai_service = (
            AIService()
        )


        self.documents = {}

        self.load_documents()


    def load_documents(self):

        metadata = (
            self.vector_store.metadata
        )


        for item in metadata:

            document_id = (
                item["document_id"]
            )


            if document_id not in self.documents:

                self.documents[document_id] = {

                    "document_id":
                        document_id,

                    "file_name":
                        "",

                    "chunks_created":
                        0

                }


            self.documents[
                document_id
            ][
                "chunks_created"
            ] += 1


    def process_document(
        self,
        file_name: str,
        file_bytes: bytes
    ):

        if not file_bytes:

            raise ValueError(
                "The uploaded file is empty"
            )


        if len(file_bytes) > MAX_FILE_SIZE:

            raise ValueError(
                "File size exceeds the allowed limit"
            )


        extension = (
            "."
            + file_name.lower().split(".")[-1]
        )


        if extension not in ALLOWED_EXTENSIONS:

            raise ValueError(
                "Only PDF and TXT files are supported"
            )


        try:

            text = extract_text(
                file_bytes,
                file_name
            )

        except Exception:

            raise RuntimeError(
                "Failed to extract text from document"
            )


        text = clean_text(text)


        if not text.strip():

            raise ValueError(
                "No extractable text was found in the document"
            )


        chunks = split_text(text)


        if not chunks:

            raise ValueError(
                "Document could not be split into chunks"
            )


        try:

            embeddings = (
                self.embedding_service
                .create_embeddings(chunks)
            )

        except Exception as exc:

            raise RuntimeError(
                f"Embedding generation failed: {str(exc)}"
            )


        document_id = uuid.uuid4().hex


        self.vector_store.add_vectors(

            embeddings=embeddings,

            document_id=document_id,

            chunks=chunks
        )


        self.documents[document_id] = {

            "document_id":
                document_id,

            "file_name":
                file_name,

            "chunks_created":
                len(chunks)

        }


        return self.documents[
            document_id
        ]


    def get_document(
        self,
        document_id: str
    ):

        return self.documents.get(
            document_id
        )


    def ask_question(
        self,
        document_id: str,
        question: str
    ):

        document = self.get_document(
            document_id
        )


        if document is None:

            raise ValueError(
                "Document not found"
            )


        if not question.strip():

            raise ValueError(
                "Question cannot be empty"
            )


        # Create embedding for question
        try:

            question_embedding = (
                self.embedding_service
                .create_embedding(question)
            )

        except Exception as exc:

            raise RuntimeError(
                f"Question embedding failed: {str(exc)}"
            )


        # Search FAISS
        try:

            results = (
                self.vector_store.search(

                    query_embedding=
                        question_embedding,

                    document_id=
                        document_id,

                    top_k=
                        TOP_K
                )
            )

        except Exception:

            raise RuntimeError(
                "Vector search failed"
            )


        if not results:

            return (
                "This information was not found "
                "in the provided document."
            )


        # Only retrieved chunks are sent to Gemini
        context = "\n\n".join(

            result["chunk"]

            for result in results

        )


        # Generate final answer
        try:

            answer = (
                self.ai_service
                .generate_answer(

                    question=question,

                    context=context,

                    system_prompt=
                        RAG_SYSTEM_PROMPT
                )
            )

        except Exception as exc:

            raise RuntimeError(
                f"AI generation failed: {str(exc)}"
            )


        return answer