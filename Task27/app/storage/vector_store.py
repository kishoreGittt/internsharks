from pathlib import Path
import json

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings


_model = None


def get_embedding_model():

    global _model

    if _model is None:

        _model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    return _model


def _get_user_dir(
    owner_id: str
):

    directory = (
        Path(settings.VECTOR_DIR)
        / str(owner_id)
    )

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    return directory


def _index_file(
    owner_id: str
):

    return (
        _get_user_dir(owner_id)
        / "vectors.npy"
    )


def _metadata_file(
    owner_id: str
):

    return (
        _get_user_dir(owner_id)
        / "metadata.json"
    )


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

    return np.load(file)


def load_metadata(
    owner_id: str
):

    file = _metadata_file(
        owner_id
    )

    if not file.exists():

        return []

    return json.loads(
        file.read_text(
            encoding="utf-8"
        )
    )


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


def add_documents(
    owner_id: str,
    document_id: str,
    chunks: list[str]
):

    if not chunks:

        raise ValueError(
            "No text chunks found."
        )

    new_vectors = create_embeddings(
        chunks
    )

    old_vectors = load_vectors(
        owner_id
    )

    old_metadata = load_metadata(
        owner_id
    )

    new_metadata = []

    for index, chunk in enumerate(
        chunks
    ):

        new_metadata.append(
            {
                "owner_id": owner_id,
                "document_id": document_id,
                "chunk_id": (
                    f"{document_id}_{index}"
                ),
                "text": chunk
            }
        )

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

    save_vectors(
        owner_id,
        vectors,
        metadata
    )

    return len(chunks)


def search(
    owner_id: str,
    query: str,
    document_ids: list[str],
    top_k: int = 3,
    min_score: float = 0.30
):

    vectors = load_vectors(
        owner_id
    )

    metadata = load_metadata(
        owner_id
    )

    if vectors.shape[0] == 0:

        return []

    if not document_ids:

        return []

    query_vector = create_embeddings(
        [query]
    )[0]

    scores = vectors @ query_vector

    ranked_indices = np.argsort(
        scores
    )[::-1]

    allowed_documents = set(
        str(document_id)
        for document_id in document_ids
    )

    results = []

    for index in ranked_indices:

        item = metadata[index]

        # -----------------------------------------
        # OWNER ISOLATION
        # -----------------------------------------

        if str(
            item.get("owner_id")
        ) != str(owner_id):

            continue

        # -----------------------------------------
        # DOCUMENT ISOLATION
        # -----------------------------------------

        if str(
            item.get("document_id")
        ) not in allowed_documents:

            continue

        score = float(
            scores[index]
        )

        if score < min_score:

            continue

        results.append(
            {
                "document_id":
                    item["document_id"],

                "chunk_id":
                    item["chunk_id"],

                "text":
                    item["text"],

                "score":
                    round(
                        score,
                        4
                    )
            }
        )

        if len(results) >= top_k:

            break

    return results