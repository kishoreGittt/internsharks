import json
import time

import httpx

from app.config import settings
from app.tools.registry import TOOLS, TOOL_FUNCTIONS


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def call_openrouter(
    messages: list,
    tools: list | None = None
):
    """Call OpenRouter using its OpenAI-compatible API."""

    if not settings.OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured."
        )

    model = settings.OPENROUTER_MODEL

    if not model:
        raise RuntimeError(
            "OPENROUTER_MODEL is not configured."
        )

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Task 27 AI Knowledge and Operations Copilot",
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    start = time.perf_counter()

    try:
        async with httpx.AsyncClient(
            timeout=90.0
        ) as client:

            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
            )

    except httpx.TimeoutException as error:
        print("\n========== OPENROUTER TIMEOUT ==========")
        print(str(error))
        print("========================================\n")

        raise RuntimeError(
            "OPENROUTER_TIMEOUT"
        ) from error

    except httpx.RequestError as error:
        print("\n======= OPENROUTER CONNECTION ERROR =======")
        print(str(error))
        print("===========================================\n")

        raise RuntimeError(
            "OPENROUTER_CONNECTION_ERROR"
        ) from error

    latency = (
        time.perf_counter() - start
    ) * 1000

    # ---------------------------------------------------------
    # HTTP error handling
    # ---------------------------------------------------------

    if response.status_code >= 400:

        print("\n==========================================")
        print("        OPENROUTER API ERROR")
        print("==========================================")
        print(f"HTTP STATUS : {response.status_code}")
        print(f"MODEL       : {model}")
        print("RESPONSE:")
        print(response.text)
        print("==========================================\n")

        if response.status_code == 401:
            raise RuntimeError(
                "OPENROUTER_INVALID_API_KEY"
            )

        if response.status_code == 403:
            raise RuntimeError(
                "OPENROUTER_ACCESS_DENIED"
            )

        if response.status_code == 404:
            raise RuntimeError(
                "OPENROUTER_MODEL_NOT_FOUND"
            )

        if response.status_code == 429:
            raise RuntimeError(
                "OPENROUTER_RATE_LIMIT"
            )

        try:
            error_data = response.json()

            provider_error = error_data.get(
                "error",
                {}
            )

            if isinstance(
                provider_error,
                dict
            ):
                provider_message = provider_error.get(
                    "message",
                    "Unknown provider error"
                )
            else:
                provider_message = str(
                    provider_error
                )

        except Exception:
            provider_message = response.text

        raise RuntimeError(
            f"OPENROUTER_ERROR_{response.status_code}: "
            f"{provider_message}"
        )

    # ---------------------------------------------------------
    # Parse JSON
    # ---------------------------------------------------------

    try:
        data = response.json()

    except ValueError as error:

        print("\n========== INVALID OPENROUTER RESPONSE ==========")
        print(response.text)
        print("=================================================\n")

        raise RuntimeError(
            "OPENROUTER_INVALID_RESPONSE"
        ) from error

    # ---------------------------------------------------------
    # Validate response
    # ---------------------------------------------------------

    choices = data.get(
        "choices"
    )

    if not choices:

        print("\n========== EMPTY OPENROUTER RESPONSE ==========")
        print(data)
        print("===============================================\n")

        raise RuntimeError(
            "OPENROUTER_EMPTY_RESPONSE"
        )

    usage = data.get(
        "usage",
        {}
    )

    return {
        "data": data,
        "latency_ms": round(
            latency,
            2
        ),
        "input_tokens": usage.get(
            "prompt_tokens",
            0
        ),
        "output_tokens": usage.get(
            "completion_tokens",
            0
        ),
    }


async def chat_with_tools(
    owner_id: str,
    messages: list,
    trace=None
):
    """Run the LLM + actual project tool-calling loop."""

    working_messages = list(
        messages
    )

    total_tool_calls = []

    total_latency = 0

    total_input_tokens = 0

    total_output_tokens = 0

    for round_number in range(
        settings.MAX_TOOL_ROUNDS
    ):

        print(
            f"AI tool round: {round_number + 1}"
        )

        result = await call_openrouter(
            working_messages,
            tools=TOOLS
        )

        total_latency += result[
            "latency_ms"
        ]

        total_input_tokens += result[
            "input_tokens"
        ]

        total_output_tokens += result[
            "output_tokens"
        ]

        data = result[
            "data"
        ]

        response_message = data[
            "choices"
        ][0].get(
            "message",
            {}
        )

        tool_calls = response_message.get(
            "tool_calls"
        )

        # -----------------------------------------------------
        # Normal final response
        # -----------------------------------------------------

        if not tool_calls:

            answer = response_message.get(
                "content"
            )

            if answer is None:
                answer = ""

            return {
                "answer": answer,
                "tool_calls": total_tool_calls,
                "latency_ms": total_latency,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }

        # -----------------------------------------------------
        # Add assistant tool call message
        # -----------------------------------------------------

        working_messages.append(
            response_message
        )

        # -----------------------------------------------------
        # Execute tools
        # -----------------------------------------------------

        for tool_call in tool_calls:

            function_data = tool_call.get(
                "function",
                {}
            )

            function_name = function_data.get(
                "name"
            )

            raw_arguments = function_data.get(
                "arguments",
                "{}"
            )

            print(
                f"Tool requested: {function_name}"
            )

            # Parse arguments
            try:

                if isinstance(
                    raw_arguments,
                    str
                ):
                    arguments = json.loads(
                        raw_arguments
                    )
                else:
                    arguments = raw_arguments

            except json.JSONDecodeError as error:

                print(
                    f"Invalid tool arguments: {error}"
                )

                tool_result = {
                    "success": False,
                    "error": "INVALID_TOOL_ARGUMENTS",
                }

                total_tool_calls.append(
                    {
                        "tool": function_name,
                        "success": False,
                    }
                )

                tool_call_id = tool_call.get(
                    "id",
                    function_name
                )

                working_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(
                            tool_result
                        ),
                    }
                )

                continue

            # -------------------------------------------------
            # Find function
            # -------------------------------------------------

            function = TOOL_FUNCTIONS.get(
                function_name
            )

            if not function:

                print(
                    f"Tool not registered: {function_name}"
                )

                tool_result = {
                    "success": False,
                    "error": "TOOL_NOT_ALLOWED",
                }

                total_tool_calls.append(
                    {
                        "tool": function_name,
                        "success": False,
                    }
                )

            else:

                try:

                    tool_start = time.perf_counter()

                    tool_result = await function(
                        owner_id,
                        arguments
                    )

                    tool_latency = (
                        time.perf_counter()
                        - tool_start
                    ) * 1000

                    total_tool_calls.append(
                        {
                            "tool": function_name,
                            "latency_ms": round(
                                tool_latency,
                                2
                            ),
                            "success": True,
                        }
                    )

                    print(
                        f"Tool completed: {function_name}"
                    )

                except Exception as error:

                    print(
                        "\n========== TOOL ERROR =========="
                    )

                    print(
                        f"Tool: {function_name}"
                    )

                    print(
                        f"Error: {error}"
                    )

                    print(
                        "================================\n"
                    )

                    tool_result = {
                        "success": False,
                        "error": "TOOL_EXECUTION_FAILED",
                    }

                    total_tool_calls.append(
                        {
                            "tool": function_name,
                            "success": False,
                        }
                    )

            # -------------------------------------------------
            # Send tool result back to model
            # -------------------------------------------------

            tool_call_id = tool_call.get(
                "id"
            )

            if not tool_call_id:
                tool_call_id = function_name

            working_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(
                        tool_result,
                        default=str
                    ),
                }
            )

    return {
        "answer": "The tool execution limit was reached.",
        "tool_calls": total_tool_calls,
        "latency_ms": total_latency,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
    }