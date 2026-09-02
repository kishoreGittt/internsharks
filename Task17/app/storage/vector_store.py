import json
import os

import faiss
import numpy as np

from app.config import VECTOR_DIR


class VectorStore:

    def __init__(self):

        os.makedirs(
            VECTOR_DIR,
            exist_ok=True
        )

        self.index = None

        self.metadata = []


        self.metadata_file = os.path.join(
            VECTOR_DIR,
            "metadata.json"
        )

        self.index_file = os.path.join(
            VECTOR_DIR,
            "index.faiss"
        )


        self.load()


    def load(self):

        if os.path.exists(
            self.index_file
        ):

            self.index = faiss.read_index(
                self.index_file
            )


        if os.path.exists(
            self.metadata_file
        ):

            with open(
                self.metadata_file,
                "r",
                encoding="utf-8"
            ) as file:

                self.metadata = json.load(
                    file
                )


    def save(self):

        if self.index is not None:

            faiss.write_index(
                self.index,
                self.index_file
            )


        with open(
            self.metadata_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.metadata,
                file,
                ensure_ascii=False,
                indent=2
            )


    def add_vectors(
        self,
        embeddings,
        document_id,
        chunks
    ):

        vectors = np.array(
            embeddings,
            dtype="float32"
        )


        if self.index is None:

            dimension = vectors.shape[1]

            self.index = faiss.IndexFlatL2(
                dimension
            )


        start_index = self.index.ntotal


        self.index.add(vectors)


        for i, chunk in enumerate(chunks):

            self.metadata.append({

                "vector_index":
                    start_index + i,

                "document_id":
                    document_id,

                "chunk":
                    chunk

            })


        self.save()


    def search(
        self,
        query_embedding,
        document_id,
        top_k
    ):

        if self.index is None:

            return []


        query_vector = np.array(
            [query_embedding],
            dtype="float32"
        )


        distances, indices = (
            self.index.search(
                query_vector,
                self.index.ntotal
            )
        )


        results = []


        for distance, index in zip(
            distances[0],
            indices[0]
        ):

            if index == -1:

                continue


            metadata = self.metadata[index]


            # Document isolation
            if (
                metadata["document_id"]
                != document_id
            ):

                continue


            results.append({

                "chunk":
                    metadata["chunk"],

                "distance":
                    float(distance)

            })


            if len(results) >= top_k:

                break


        return results