import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

import requests

from app.agent.registry import (
    TOOL_DEFINITIONS,
    get_tool_function,
)
from app.config import (
    MAX_AGENT_STEPS,
    OPENROUTER_API_KEY,
    OPENROUTER_FALLBACK_MODELS,
    OPENROUTER_MODEL,
    OPENROUTER_URL,
)
from app.prompts.agent_prompt import AGENT_SYSTEM_PROMPT
from app.storage.run_store import runs


class AgentRunner:

    def __init__(self):
        self.primary_model = OPENROUTER_MODEL

        # Create a unique list of models
        self.models = []

        for model in [self.primary_model] + OPENROUTER_FALLBACK_MODELS:
            if model and model not in self.models:
                self.models.append(model)

    # =========================================================
    # MAIN AGENT LOOP
    # =========================================================

    def run(self, goal: str) -> Dict[str, Any]:

        run_id = str(uuid.uuid4())

        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": AGENT_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": goal,
            },
        ]

        execution_trace = []
        tools_used = []

        for step_number in range(1, MAX_AGENT_STEPS + 1):

            # -------------------------------------------------
            # Ask OpenRouter what to do next
            # -------------------------------------------------

            response, actual_model = (
                self._call_openrouter_with_fallback(messages)
            )

            print(
                f"[Agent] Step {step_number} | "
                f"Model: {actual_model}"
            )

            message = self._extract_message(response)

            # -------------------------------------------------
            # Check if AI wants to execute tools
            # -------------------------------------------------

            tool_calls = message.get("tool_calls", [])

            # -------------------------------------------------
            # No tool call = final answer
            # -------------------------------------------------

            if not tool_calls:

                final_answer = message.get("content")

                if not final_answer:
                    final_answer = (
                        "The agent completed the requested actions."
                    )

                status = self._calculate_status(
                    execution_trace,
                    final_answer,
                )

                run_data = {
                    "run_id": run_id,
                    "goal": goal,
                    "status": status,
                    "final_result": final_answer,
                    "tools_used": tools_used,
                    "execution_trace": execution_trace,
                    "created_at": datetime.now(
                        timezone.utc
                    ).isoformat(),
                }

                runs[run_id] = run_data

                return run_data

            # -------------------------------------------------
            # Add assistant message containing tool calls
            # -------------------------------------------------

            assistant_message = {
                "role": "assistant",
                "content": message.get("content"),
                "tool_calls": tool_calls,
            }

            messages.append(assistant_message)

            # -------------------------------------------------
            # Execute tools
            # -------------------------------------------------

            for tool_call in tool_calls:

                function_data = tool_call.get(
                    "function",
                    {},
                )

                tool_name = function_data.get("name")

                tool_call_id = tool_call.get("id")

                raw_arguments = function_data.get(
                    "arguments",
                    "{}",
                )

                # =================================================
                # VALIDATE TOOL NAME
                # =================================================

                if not tool_name:

                    result = {
                        "success": False,
                        "error": (
                            "AI returned a tool call "
                            "without a tool name."
                        ),
                    }

                    execution_trace.append(
                        self._trace_entry(
                            step_number,
                            "unknown",
                            {},
                            result,
                            False,
                        )
                    )

                    if tool_call_id:
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": json.dumps(result),
                            }
                        )

                    continue

                # =================================================
                # PARSE TOOL ARGUMENTS
                # =================================================

                try:

                    arguments = json.loads(
                        raw_arguments
                    )

                    if not isinstance(arguments, dict):
                        raise ValueError(
                            "Tool arguments must be "
                            "a JSON object."
                        )

                except (
                    json.JSONDecodeError,
                    ValueError,
                ) as exc:

                    result = {
                        "success": False,
                        "error": (
                            f"Invalid tool arguments: {str(exc)}"
                        ),
                    }

                    execution_trace.append(
                        self._trace_entry(
                            step_number,
                            tool_name,
                            {},
                            result,
                            False,
                        )
                    )

                    if tool_call_id:
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": json.dumps(result),
                            }
                        )

                    continue

                # =================================================
                # GET TOOL FROM CONTROLLED REGISTRY
                # =================================================

                try:

                    tool_function = get_tool_function(
                        tool_name
                    )

                except Exception as exc:

                    result = {
                        "success": False,
                        "error": str(exc),
                    }

                    execution_trace.append(
                        self._trace_entry(
                            step_number,
                            tool_name,
                            arguments,
                            result,
                            False,
                        )
                    )

                    if tool_call_id:
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": json.dumps(result),
                            }
                        )

                    continue

                # =================================================
                # EXECUTE TOOL
                # =================================================

                try:

                    result = tool_function(
                        **arguments
                    )

                    if isinstance(result, dict):

                        success = result.get(
                            "success",
                            True,
                        )

                    else:

                        success = True

                except Exception as exc:

                    result = {
                        "success": False,
                        "error": str(exc),
                    }

                    success = False

                # =================================================
                # RECORD EXECUTION TRACE
                # =================================================

                execution_trace.append(
                    self._trace_entry(
                        step_number,
                        tool_name,
                        arguments,
                        result,
                        success,
                    )
                )

                if tool_name not in tools_used:
                    tools_used.append(tool_name)

                # =================================================
                # RETURN TOOL RESULT TO AI
                # =================================================

                if tool_call_id:

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": json.dumps(
                                result
                            ),
                        }
                    )

        # =====================================================
        # MAXIMUM STEP LIMIT
        # =====================================================

        final_result = (
            f"The agent stopped because the maximum "
            f"number of steps ({MAX_AGENT_STEPS}) "
            f"was reached."
        )

        run_data = {
            "run_id": run_id,
            "goal": goal,
            "status": "partially_completed",
            "final_result": final_result,
            "tools_used": tools_used,
            "execution_trace": execution_trace,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        runs[run_id] = run_data

        return run_data

    # =========================================================
    # OPENROUTER CALL WITH FALLBACK
    # =========================================================

    def _call_openrouter_with_fallback(
        self,
        messages: List[Dict[str, Any]],
    ):

        if not OPENROUTER_API_KEY:

            raise RuntimeError(
                "OPENROUTER_API_KEY is not configured."
            )

        if not self.models:

            raise RuntimeError(
                "No OpenRouter models are configured."
            )

        # -----------------------------------------------------
        # Use OpenRouter's model fallback feature
        # -----------------------------------------------------

        payload = {
            "model": self.models[0],

            "models": self.models,

            "messages": messages,

            "tools": TOOL_DEFINITIONS,

            "tool_choice": "auto",
        }

        headers = {
            "Authorization": (
                f"Bearer {OPENROUTER_API_KEY}"
            ),
            "Content-Type": "application/json",
        }

        try:

            response = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=120,
            )

        except requests.RequestException as exc:

            raise RuntimeError(
                "Unable to connect to OpenRouter."
            ) from exc

        # =====================================================
        # SUCCESS
        # =====================================================

        if response.status_code == 200:

            try:

                data = response.json()

            except ValueError as exc:

                raise RuntimeError(
                    "OpenRouter returned invalid JSON."
                ) from exc

            actual_model = data.get(
                "model",
                self.models[0],
            )

            print(
                f"[OpenRouter] Model used: "
                f"{actual_model}"
            )

            return data, actual_model

        # =====================================================
        # AUTHENTICATION ERROR
        # =====================================================

        if response.status_code == 401:

            raise RuntimeError(
                "OpenRouter authentication failed. "
                "Check your OPENROUTER_API_KEY."
            )

        # =====================================================
        # RATE LIMIT
        # =====================================================

        if response.status_code == 429:

            raise RuntimeError(
                "OpenRouter rate limit reached for "
                "the configured models. "
                "Please try again later."
            )

        # =====================================================
        # MODEL / TOOL ENDPOINT NOT AVAILABLE
        # =====================================================

        if response.status_code == 404:

            try:
                error_data = response.json()

            except ValueError:
                error_data = response.text

            raise RuntimeError(
                "OpenRouter model or tool endpoint "
                "is unavailable. "
                f"Configured models: {self.models}. "
                f"Response: {error_data}"
            )

        # =====================================================
        # SERVER ERROR
        # =====================================================

        if response.status_code in (
            500,
            502,
            503,
            504,
        ):

            raise RuntimeError(
                "OpenRouter service is temporarily "
                "unavailable. Please try again."
            )

        # =====================================================
        # OTHER ERROR
        # =====================================================

        try:
            error_data = response.json()

        except ValueError:
            error_data = response.text

        raise RuntimeError(
            f"OpenRouter API error "
            f"(HTTP {response.status_code}): "
            f"{error_data}"
        )

    # =========================================================
    # EXTRACT ASSISTANT MESSAGE
    # =========================================================

    @staticmethod
    def _extract_message(
        response: Dict[str, Any],
    ) -> Dict[str, Any]:

        choices = response.get("choices")

        if not choices:

            raise RuntimeError(
                "OpenRouter returned no choices."
            )

        message = choices[0].get(
            "message"
        )

        if not message:

            raise RuntimeError(
                "OpenRouter returned no assistant message."
            )

        return message

    # =========================================================
    # EXECUTION TRACE
    # =========================================================

    @staticmethod
    def _trace_entry(
        step_number: int,
        tool: str,
        arguments: Dict[str, Any],
        result: Any,
        success: bool,
    ) -> Dict[str, Any]:

        return {
            "step": step_number,
            "tool": tool,
            "arguments": arguments,
            "result": result,
            "success": success,
        }

    # =========================================================
    # CALCULATE FINAL STATUS
    # =========================================================

    @staticmethod
    def _calculate_status(
        execution_trace: List[Dict[str, Any]],
        final_answer: str,
    ) -> str:

        # No tools means the agent simply answered
        if not execution_trace:
            return "completed"

        successful_steps = sum(
            1
            for step in execution_trace
            if step.get("success") is True
        )

        failed_steps = sum(
            1
            for step in execution_trace
            if step.get("success") is False
        )

        # All tools succeeded
        if failed_steps == 0:
            return "completed"

        # Some succeeded and some failed
        if successful_steps > 0:
            return "partially_completed"

        # Everything failed
        return "failed"