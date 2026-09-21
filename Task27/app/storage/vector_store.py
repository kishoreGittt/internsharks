from pathlib import Path
import json

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings


_model = None


# =========================================================
# EMBEDDING MODEL
# =========================================================

def get_embedding_model():
    global _model

    if _model is None:

        print("Loading embedding model...")

        _model = SentenceTransformer(
            settings.EMBEDDING_MODEL
        )

        print(
            f"Embedding model loaded: "
            f"{settings.EMBEDDING_MODEL}"
        )

    return _model


# =========================================================
# USER VECTOR DIRECTORY
# =========================================================

def _get_user_dir(
    owner_id: str
):
    directory = (
        Path(settings.VECTOR_DIR)
        / owner_id
    )

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    return directory


# =========================================================
# VECTOR FILE
# =========================================================

def _index_file(
    owner_id: str
):
    return (
        _get_user_dir(owner_id)
        / "vectors.npy"
    )


# =========================================================
# METADATA FILE
# =========================================================

def _metadata_file(
    owner_id: str
):
    return (
        _get_user_dir(owner_id)
        / "metadata.json"
    )


# =========================================================
# CREATE EMBEDDINGS
# =========================================================

def create_embeddings(
    texts: list[str]
):

    if not texts:
        return np.empty(
            (0, 384),
            dtype=np.float32
        )

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embeddings.astype(
        np.float32
    )


# =========================================================
# LOAD VECTORS
# =========================================================

def load_vectors(
    owner_id: str
):

    file = _index_file(
        owner_id
    )

    if not file.exists():

        return np.empty(
            (0, 384),
            dtype=np.float32
        )

    vectors = np.load(
        file
    )

    return vectors.astype(
        np.float32
    )


# =========================================================
# LOAD METADATA
# =========================================================

def load_metadata(
    owner_id: str
):

    file = _metadata_file(
        owner_id
    )

    if not file.exists():

        return []

    try:

        return json.loads(
            file.read_text(
                encoding="utf-8"
            )
        )

    except Exception as error:

        print(
            f"Could not load vector metadata: {error}"
        )

        return []


# =========================================================
# SAVE VECTORS + METADATA
# =========================================================

def save_vectors(
    owner_id: str,
    vectors,
    metadata
):

    np.save(
        _index_file(owner_id),
        vectors
    )

    _metadata_file(
        owner_id
    ).write_text(
        json.dumps(
            metadata,
            indent=2
        ),
        encoding="utf-8"
    )


# =========================================================
# ADD DOCUMENT
# =========================================================

def add_documents(
    owner_id: str,
    document_id: str,
    chunks: list[str]
):

    if not chunks:

        raise ValueError(
            "No text chunks found."
        )

    print("\n==========================================")
    print("         VECTOR INDEXING")
    print("==========================================")
    print(f"Owner ID      : {owner_id}")
    print(f"Document ID   : {document_id}")
    print(f"Chunks        : {len(chunks)}")

    # -----------------------------------------------------
    # Create embeddings
    # -----------------------------------------------------

    new_vectors = create_embeddings(
        chunks
    )

    # -----------------------------------------------------
    # Load existing vectors
    # -----------------------------------------------------

    old_vectors = load_vectors(
        owner_id
    )

    old_metadata = load_metadata(
        owner_id
    )

    # -----------------------------------------------------
    # Validate old index
    # -----------------------------------------------------

    if old_vectors.shape[0] != len(old_metadata):

        print(
            "WARNING: Vector/metadata count mismatch."
        )

        print(
            f"Vectors  : {old_vectors.shape[0]}"
        )

        print(
            f"Metadata : {len(old_metadata)}"
        )

        # Rebuild from the new document instead of
        # combining corrupted index data.
        old_vectors = np.empty(
            (0, new_vectors.shape[1]),
            dtype=np.float32
        )

        old_metadata = []

    # -----------------------------------------------------
    # Create metadata
    # -----------------------------------------------------

    new_metadata = []

    for index, chunk in enumerate(chunks):

        new_metadata.append(
            {
                "document_id": document_id,
                "chunk_id": (
                    f"{document_id}_{index}"
                ),
                "text": chunk
            }
        )

    # -----------------------------------------------------
    # Combine
    # -----------------------------------------------------

    if old_vectors.shape[0] > 0:

        vectors = np.vstack(
            [
                old_vectors,
                new_vectors
            ]
        )

        metadata = (
            old_metadata
            + new_metadata
        )

    else:

        vectors = new_vectors

        metadata = new_metadata

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    save_vectors(
        owner_id=owner_id,
        vectors=vectors,
        metadata=metadata
    )

    print(
        f"Total vectors : {vectors.shape[0]}"
    )

    print(
        f"Total metadata: {len(metadata)}"
    )

    print("Vector indexing completed.")

    print("==========================================\n")

    return len(chunks)


# =========================================================
# SEARCH
# =========================================================

def search(
    owner_id: str,
    query: str,
    document_ids: list[str],
    top_k: int = 3,
    min_score: float = 0.15
):

    print("\n==========================================")
    print("            VECTOR SEARCH")
    print("==========================================")
    print(f"Owner ID     : {owner_id}")
    print(f"Query        : {query}")
    print(f"Document IDs : {document_ids}")
    print(f"Top K        : {top_k}")

    # -----------------------------------------------------
    # Load vectors
    # -----------------------------------------------------

    vectors = load_vectors(
        owner_id
    )

    metadata = load_metadata(
        owner_id
    )

    print(
        f"Vectors found : {vectors.shape[0]}"
    )

    print(
        f"Metadata found: {len(metadata)}"
    )

    # -----------------------------------------------------
    # No vectors
    # -----------------------------------------------------

    if vectors.shape[0] == 0:

        print(
            "No vectors found for this user."
        )

        return []

    # -----------------------------------------------------
    # Validate vector/metadata count
    # -----------------------------------------------------

    if vectors.shape[0] != len(metadata):

        print(
            "Vector/metadata count mismatch."
        )

        return []

    # -----------------------------------------------------
    # Validate document IDs
    # -----------------------------------------------------

    allowed_documents = set(
        document_ids
    )

    if not allowed_documents:

        print(
            "No document IDs supplied."
        )

        return []

    # -----------------------------------------------------
    # Create query embedding
    # -----------------------------------------------------

    query_vector = create_embeddings(
        [query]
    )[0]

    # -----------------------------------------------------
    # Cosine similarity
    #
    # Vectors and query are normalized, therefore:
    #
    # cosine similarity = dot product
    # -----------------------------------------------------

    scores = vectors @ query_vector

    ranked_indices = np.argsort(
        scores
    )[::-1]

    results = []

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    for index in ranked_indices:

        item = metadata[index]

        item_document_id = item.get(
            "document_id"
        )

        # -----------------------------------------------
        # IMPORTANT:
        # Only search selected documents.
        # -----------------------------------------------

        if item_document_id not in allowed_documents:

            continue

        score = float(
            scores[index]
        )

        print(
            f"Candidate: "
            f"{item.get('chunk_id')} "
            f"score={score:.4f}"
        )

        # -----------------------------------------------
        # Similarity threshold
        # -----------------------------------------------

        if score < min_score:

            continue

        results.append(
            {
                "document_id": item_document_id,

                "chunk_id": item.get(
                    "chunk_id"
                ),

                "text": item.get(
                    "text",
                    ""
                ),

                "score": round(
                    score,
                    4
                )
            }
        )

        if len(results) >= top_k:

            break

    # -----------------------------------------------------
    # FALLBACK
    #
    # If the selected document has chunks but all scores
    # are below the threshold, return the best matching
    # selected chunks instead of returning nothing.
    # -----------------------------------------------------

    if not results:

        print(
            "No chunks passed similarity threshold."
        )

        fallback_results = []

        for index in ranked_indices:

            item = metadata[index]

            if item.get(
                "document_id"
            ) not in allowed_documents:

                continue

            score = float(
                scores[index]
            )

            fallback_results.append(
                {
                    "document_id": item.get(
                        "document_id"
                    ),

                    "chunk_id": item.get(
                        "chunk_id"
                    ),

                    "text": item.get(
                        "text",
                        ""
                    ),

                    "score": round(
                        score,
                        4
                    )
                }
            )

            if len(
                fallback_results
            ) >= top_k:

                break

        results = fallback_results

    print(
        f"Final results: {len(results)}"
    )

    for result in results:

        print(
            f"  {result['chunk_id']} "
            f"score={result['score']}"
        )

    print("==========================================\n")

    return results