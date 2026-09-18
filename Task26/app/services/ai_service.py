import asyncio
import json
from typing import Any

import httpx

from app.models.analysis import (
    DocumentAnalysisResult,
    KeyPointsResult,
    SummaryResult,
)
from app.prompts.document_analysis import (
    build_document_prompt,
)


class AIService:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        simulated_delay: float = 0,
        simulate_failure: bool = False,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.simulated_delay = simulated_delay
        self.simulate_failure = simulate_failure

    async def analyze_document(
        self,
        analysis_type: str,
        document_text: str,
    ) -> dict[str, Any]:
        if self.simulated_delay > 0:
            await asyncio.sleep(self.simulated_delay)

        if self.simulate_failure:
            raise RuntimeError("Simulated AI failure")

        prompt = build_document_prompt(
            analysis_type=analysis_type,
            document_text=document_text,
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a document analysis assistant. "
                        "Return valid JSON only."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.2,
            "response_format": {
                "type": "json_object",
            },
        }

        endpoint = f"{self.base_url}/chat/completions"

        timeout = httpx.Timeout(
            connect=20.0,
            read=120.0,
            write=30.0,
            pool=20.0,
        )

        async with httpx.AsyncClient(
            timeout=timeout,
        ) as client:
            response = await client.post(
                endpoint,
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenRouter request failed "
                f"with status {response.status_code}: "
                f"{response.text[:500]}"
            )

        try:
            response_data = response.json()

            content = response_data["choices"][0]["message"]["content"]

        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "Invalid response received from OpenRouter"
            ) from exc

        try:
            parsed_content = json.loads(content)

        except (json.JSONDecodeError, TypeError) as exc:
            raise RuntimeError(
                "OpenRouter did not return valid JSON"
            ) from exc

        return self._validate_result(
            analysis_type=analysis_type,
            data=parsed_content,
        )

    def _validate_result(
        self,
        analysis_type: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        if analysis_type == "summary":
            result = SummaryResult.model_validate(data)

        elif analysis_type == "key_points":
            result = KeyPointsResult.model_validate(data)

        elif analysis_type == "document_analysis":
            result = DocumentAnalysisResult.model_validate(data)

        else:
            raise ValueError("Unsupported analysis type")

        return result.model_dump()