import requests

from app.config import (
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL
)


class EmbeddingService:

    def __init__(self):

        self.api_key = GEMINI_API_KEY

        self.model = GEMINI_EMBEDDING_MODEL

        self.base_url = (
            "https://generativelanguage.googleapis.com/v1beta"
        )


    def _headers(self):

        return {
            "Content-Type": "application/json",

            "x-goog-api-key": self.api_key
        }


    def create_embedding(
        self,
        text: str
    ):

        if not self.api_key:

            raise RuntimeError(
                "Gemini API key is not configured"
            )


        url = (
            f"{self.base_url}/"
            f"{self.model}:embedContent"
        )


        payload = {

            "content": {

                "parts": [

                    {
                        "text": text
                    }

                ]

            }

        }


        response = requests.post(

            url,

            headers=self._headers(),

            json=payload,

            timeout=60
        )


        if response.status_code == 401:

            raise RuntimeError(
                "Invalid Gemini API key"
            )


        if response.status_code == 429:

            raise RuntimeError(
                "Gemini embedding rate limit reached"
            )


        if response.status_code != 200:

            print(
                "Gemini embedding error:",
                response.text
            )

            raise RuntimeError(
                f"Gemini embedding API failed: "
                f"{response.status_code}"
            )


        data = response.json()


        try:

            return data[
                "embedding"
            ][
                "values"
            ]

        except (
            KeyError,
            TypeError
        ):

            raise RuntimeError(
                "Invalid embedding response from Gemini"
            )


    def create_embeddings(
        self,
        texts
    ):

        embeddings = []


        for text in texts:

            embedding = self.create_embedding(
                text
            )

            embeddings.append(
                embedding
            )


        return embeddings