import requests

from app.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)


class AIService:

    def __init__(self):

        self.api_key = GEMINI_API_KEY
        self.model = GEMINI_MODEL
        self.base_url = (
            "https://generativelanguage.googleapis.com/v1beta"
        )

    def _headers(self):

        return {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

    def generate_answer(
        self,
        question: str,
        context: str,
        system_prompt: str
    ):

        if not self.api_key:
            raise RuntimeError(
                "Gemini API key is not configured"
            )

        url = (
            f"{self.base_url}/"
            f"{self.model}:generateContent"
        )

        final_prompt = system_prompt.format(
            context=context,
            question=question
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": final_prompt
                        }
                    ]
                }
            ]
        }

        try:

            response = requests.post(
                url,
                headers=self._headers(),
                json=payload,
                timeout=60
            )

        except requests.RequestException:

            raise RuntimeError(
                "Unable to connect to Gemini API"
            )

        if response.status_code == 400:
            raise RuntimeError(
                "Invalid request sent to Gemini API"
            )

        if response.status_code == 401:
            raise RuntimeError(
                "Invalid Gemini API key"
            )

        if response.status_code == 403:
            raise RuntimeError(
                "Gemini API access is not allowed"
            )

        if response.status_code == 404:
            raise RuntimeError(
                f"Gemini model '{self.model}' "
                "is not available"
            )

        if response.status_code == 429:
            raise RuntimeError(
                "Gemini API rate limit reached"
            )

        if response.status_code != 200:

            print(
                "Gemini generation error:",
                response.text
            )

            raise RuntimeError(
                f"Gemini API failed: "
                f"{response.status_code}"
            )

        try:

            data = response.json()

            answer = (
                data["candidates"][0]
                ["content"]["parts"][0]["text"]
            )

        except (
            KeyError,
            IndexError,
            TypeError,
            ValueError
        ):

            raise RuntimeError(
                "Invalid response from Gemini"
            )

        if not answer or not answer.strip():

            raise RuntimeError(
                "Gemini returned an empty answer"
            )

        return answer.strip()