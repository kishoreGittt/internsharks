from groq import Groq
from app.config import settings


class AIServiceError(Exception):
    """Base exception for AI service errors."""
    pass


class AIRateLimitError(AIServiceError):
    """Raised when Groq rate limit is exceeded."""
    pass


class AIServiceUnavailableError(AIServiceError):
    """Raised when Groq is unavailable."""
    pass


class AIService:
    def __init__(self):
        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

    def generate_response(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful AI assistant. "
                            "Give clear and simple answers."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response = completion.choices[0].message.content

            if not response:
                raise AIServiceUnavailableError()

            return response

        except Exception as exc:
            status_code = getattr(exc, "status_code", None)

            if status_code == 429:
                raise AIRateLimitError() from exc

            if status_code in (401, 403):
                raise AIServiceUnavailableError() from exc

            raise AIServiceUnavailableError() from exc


ai_service = AIService()