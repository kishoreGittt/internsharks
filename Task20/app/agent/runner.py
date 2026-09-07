import json
import uuid
from typing import Any, Dict, List

import requests

from app.agent.registry import (
    TOOL_DEFINITIONS,
    get_tool_function
)

from app.config import (
    MAX_AGENT_STEPS,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_URL
)

from app.prompts.agent_prompt import (
    AGENT_SYSTEM_PROMPT
)

from app.storage.run_store import runs


class AgentRunner:

    def __init__(self):
        self.max_steps = MAX_AGENT_STEPS

    def _validate_configuration(self):

        if not OPENROUTER_API_KEY:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not configured."
            )

        if not OPENROUTER_MODEL:
            raise RuntimeError(
                "OPENROUTER_MODEL is not configured."
            )

    def _call_openrouter(
        self,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        self._validate_configuration()

        headers = {
            "Authorization": (
                f"Bearer {OPENROUTER_API_KEY}"
            ),
            "Content-Type": "application/json",
            "X-Title": "Task 20 Goal Based AI Agent"
        }

        payload = {
            "model": OPENROUTER_MODEL,
            "messages": messages,
            "tools": TOOL_DEFINITIONS,
            "tool_choice": "auto"
        }

        try:

            response = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=90
            )

        except requests.RequestException as exc:

            raise RuntimeError(
                f"Unable to connect to OpenRouter: {exc}"
            )

        if response.status_code == 401:

            raise RuntimeError(
                "OpenRouter authentication failed. "
                "Check OPENROUTER_API_KEY."
            )

        if response.status_code == 404:

            raise RuntimeError(
                "OpenRouter model or tool endpoint is unavailable. "
                "Check OPENROUTER_MODEL and confirm tool support."
            )

        if response.status_code == 429:

            raise RuntimeError(
                "OpenRouter rate limit reached."
            )

        if response.status_code >= 400:

            try:
                error_data = response.json()
            except ValueError:
                error_data = response.text

            raise RuntimeError(
                f"OpenRouter API error {response.status_code}: "
                f"{error_data}"
            )

        try:
            return response.json()

        except ValueError:

            raise RuntimeError(
                "OpenRouter returned invalid JSON."
            )

    def _execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:

        try:

            tool_function = get_tool_function(
                tool_name
            )

            result = tool_function(
                **arguments
            )

            return {
                "success": True,
                "result": result
            }

        except TypeError as exc:

            return {
                "success": False,
                "error": (
                    "Invalid tool arguments: "
                    f"{str(exc)}"
                )
            }

        except ValueError as exc:

            return {
                "success": False,
                "error": str(exc)
            }

        except Exception as exc:

            return {
                "success": False,
                "error": (
                    "Tool execution failed."
                )
            }

    def run(
        self,
        goal: str
    ) -> Dict[str, Any]:

        run_id = f"run_{uuid.uuid4().hex[:12]}"

        execution_trace = []

        tools_used = []

        messages = [
            {
                "role": "system",
                "content": AGENT_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": goal
            }
        ]

        runs[run_id] = {
            "run_id": run_id,
            "goal": goal,
            "status": "running",
            "steps": []
        }

        for step_number in range(
            1,
            self.max_steps + 1
        ):

            response = self._call_openrouter(
                messages
            )

            choices = response.get(
                "choices",
                []
            )

            if not choices:

                raise RuntimeError(
                    "Invalid AI response: "
                    "no choices returned."
                )

            message = choices[0].get(
                "message",
                {}
            )

            tool_calls = message.get(
                "tool_calls"
            )

            # No more tools means the model
            # has produced the final response.
            if not tool_calls:

                final_response = (
                    message.get("content")
                    or "Agent completed execution."
                )

                runs[run_id]["status"] = (
                    "completed"
                )

                runs[run_id]["steps"] = (
                    execution_trace
                )

                return {
                    "run_id": run_id,
                    "goal": goal,
                    "status": self._calculate_status(
                        execution_trace
                    ),
                    "steps_executed": len(
                        execution_trace
                    ),
                    "tools_used": tools_used,
                    "response": final_response
                }

            # Keep the assistant tool-call message
            # in the conversation.
            messages.append(message)

            for tool_call in tool_calls:

                if len(execution_trace) >= self.max_steps:

                    break

                function_data = (
                    tool_call.get(
                        "function",
                        {}
                    )
                )

                tool_name = function_data.get(
                    "name"
                )

                raw_arguments = (
                    function_data.get(
                        "arguments",
                        "{}"
                    )
                )

                tool_call_id = (
                    tool_call.get("id")
                )

                if not tool_name:

                    result = {
                        "success": False,
                        "error": (
                            "AI returned a tool call "
                            "without a tool name."
                        )
                    }

                    tool_name = "unknown"

                    arguments = {}

                else:

                    try:

                        arguments = json.loads(
                            raw_arguments
                        )

                    except json.JSONDecodeError:

                        result = {
                            "success": False,
                            "error": (
                                "Invalid JSON arguments "
                                "generated by AI."
                            )
                        }

                        arguments = {}

                    else:

                        result = self._execute_tool(
                            tool_name,
                            arguments
                        )

                status = (
                    "success"
                    if result.get("success")
                    else "failed"
                )

                trace_item = {
                    "step": len(
                        execution_trace
                    ) + 1,
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": result,
                    "status": status
                }

                execution_trace.append(
                    trace_item
                )

                tools_used.append(
                    tool_name
                )

                runs[run_id]["steps"] = (
                    execution_trace
                )

                # Return actual backend result
                # to the model.
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(
                            result,
                            default=str
                        )
                    }
                )

        # Maximum step count reached.
        runs[run_id]["status"] = (
            "partially_completed"
        )

        runs[run_id]["steps"] = (
            execution_trace
        )

        return {
            "run_id": run_id,
            "goal": goal,
            "status": "partially_completed",
            "steps_executed": len(
                execution_trace
            ),
            "tools_used": tools_used,
            "response": (
                "The agent stopped because the "
                f"maximum step limit of "
                f"{self.max_steps} was reached. "
                "Some operations may have been completed."
            )
        }

    @staticmethod
    def _calculate_status(
        trace: List[Dict[str, Any]]
    ) -> str:

        if not trace:
            return "completed"

        failures = [
            item
            for item in trace
            if item["status"] == "failed"
        ]

        if failures and len(failures) == len(trace):
            return "failed"

        if failures:
            return "partially_completed"

        return "completed"