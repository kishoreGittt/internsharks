import httpx

from app.config import settings


class AIServiceError(Exception):
    pass


class AIRateLimitError(AIServiceError):
    pass


class AIAuthenticationError(AIServiceError):
    pass


class AIServiceUnavailableError(AIServiceError):
    pass


class AIService:

    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY

    async def generate_response(self, prompt: str) -> str:

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "liquid/lfm-2.5-2.6b:free",
            "messages": [
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
        }

        try:

            async with httpx.AsyncClient(timeout=30.0) as client:

                response = await client.post(
                    self.OPENROUTER_URL,
                    headers=headers,
                    json=payload
                )

            # Rate limit
            if response.status_code == 429:
                print("OpenRouter API Error: Rate limit exceeded")
                raise AIRateLimitError()

            # Invalid or unauthorized API key
            if response.status_code in (401, 403):
                print(
                    f"OpenRouter API Error: "
                    f"Authentication failed ({response.status_code})"
                )
                raise AIAuthenticationError()

            # OpenRouter server error
            if response.status_code >= 500:
                print(
                    f"OpenRouter API Error: "
                    f"Server error ({response.status_code})"
                )
                raise AIServiceUnavailableError()

            # Other OpenRouter errors
            if response.status_code != 200:
                print(
                    f"OpenRouter API Error: "
                    f"{response.status_code} - {response.text}"
                )
                raise AIServiceUnavailableError()

            # Convert response to JSON
            data = response.json()

            # Get choices
            choices = data.get("choices")

            if not choices:
                print("OpenRouter API Error: No choices returned")
                raise AIServiceUnavailableError()

            # Get message
            message = choices[0].get("message", {})

            # Get generated content
            content = message.get("content")

            if not content:
                print("OpenRouter API Error: Empty AI response")
                raise AIServiceUnavailableError()

            return content

        # Request timeout
        except httpx.TimeoutException as exc:
            print(f"OpenRouter API Timeout: {exc}")
            raise AIServiceUnavailableError() from exc

        # Connection/request error
        except httpx.RequestError as exc:
            print(f"OpenRouter Connection Error: {exc}")
            raise AIServiceUnavailableError() from exc


ai_service = AIService()