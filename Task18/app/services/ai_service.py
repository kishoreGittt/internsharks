from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_MODEL


class AIService:

    def __init__(self):
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    def generate_response(
        self,
        contents,
        tools=None
    ):

        config = types.GenerateContentConfig()

        if tools:
            config.tools = tools

        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=config
        )

        return response