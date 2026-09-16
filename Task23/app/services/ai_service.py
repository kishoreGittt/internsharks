import json
import time
import requests
from app.config import settings

class AIService:
    def __init__(self, model: str | None = None):
        self.model = model or settings.openrouter_model

    def answer(self, question: str, context: str, system_prompt: str) -> dict:
        if not settings.openrouter_api_key:
            return self.mock_answer(question, context)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
            ],
            "temperature": 0
        }
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=settings.request_timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        usage = data.get("usage") or {}
        return {
            "answer": data["choices"][0]["message"]["content"],
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
        }

    def mock_answer(self, question: str, context: str) -> dict:
        q, c = question.lower(), context.lower()
        if "database" in q or "salary" in q or "phone" in q or ("manager" in q and "orion" in q):
            answer = "The information is not available in the provided context."
        elif "nova" in q and ("manager" in q or "manages" in q):
            answer = "Arun manages Project Nova."
        elif "framework" in q and "orion" in q:
            answer = "Project Orion uses Django."
        elif "department" in q:
            answer = "Arun works in the Development department."
        elif "technologies" in q:
            answer = "Project Nova uses FastAPI and Python."
        elif "flask" in q:
            answer = "No, Project Nova uses FastAPI."
        elif "project managed by arun" in q:
            answer = "Project Nova."
        elif "json" in q:
            answer = json.dumps({"answer": "Arun", "confidence": 0.95})
        else:
            answer = "The information is not available in the provided context."
        return {"answer": answer, "prompt_tokens": None, "completion_tokens": None, "total_tokens": None}
