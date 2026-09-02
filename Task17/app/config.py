import os

from dotenv import load_dotenv


load_dotenv()


# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "models/gemini-3.6-flash"
)

GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "models/gemini-embedding-2-preview"
)


# RAG settings
CHUNK_SIZE = int(
    os.getenv("CHUNK_SIZE", "800")
)

CHUNK_OVERLAP = int(
    os.getenv("CHUNK_OVERLAP", "100")
)

TOP_K = int(
    os.getenv("TOP_K", "3")
)

MAX_FILE_SIZE = int(
    os.getenv("MAX_FILE_SIZE", "10485760")
)


# Storage
DOCUMENT_DIR = "data/documents"

VECTOR_DIR = "vector_data"