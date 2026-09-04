import json
import requests

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_URL,
    OPENROUTER_MODEL,
    OPENROUTER_FALLBACK_MODELS,
    MAX_TOOL_ROUNDS
)

from app.prompts.employee_assistant_prompt import SYSTEM_PROMPT
from app.storage.chat_memory import get_history, add_message
from app.tools.registry import execute_tool


class AssistantService:

    def __init__(self):

        if not OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY is not configured."
            )

        if not OPENROUTER_URL:
            raise ValueError(
                "OPENROUTER_URL is not configured."
            )

    def get_tools(self):

        return [
            {
                "type": "function",
                "function": {
                    "name": "get_employee",
                    "description": "Get employee information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "integer",
                                "description": "Employee ID"
                            }
                        },
                        "required": ["employee_id"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "get_leave_balance",
                    "description": (
                        "Get employee casual and sick leave balance."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "integer",
                                "description": "Employee ID"
                            }
                        },
                        "required": ["employee_id"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "get_company_holidays",
                    "description": (
                        "Get company holidays. "
                        "Dates are optional."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "Start date YYYY-MM-DD"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date YYYY-MM-DD"
                            }
                        }
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "apply_leave",
                    "description": (
                        "Apply for casual or sick leave."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "integer"
                            },
                            "leave_type": {
                                "type": "string",
                                "enum": ["casual", "sick"]
                            },
                            "start_date": {
                                "type": "string",
                                "description": (
                                    "Start date YYYY-MM-DD"
                                )
                            },
                            "end_date": {
                                "type": "string",
                                "description": (
                                    "End date YYYY-MM-DD"
                                )
                            },
                            "reason": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "employee_id",
                            "leave_type",
                            "start_date",
                            "end_date",
                            "reason"
                        ]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "get_leave_requests",
                    "description": (
                        "Get previous leave requests "
                        "for an employee."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "integer"
                            }
                        },
                        "required": ["employee_id"]
                    }
                }
            }
        ]

    def get_tool_names(self):

        return {
            "get_employee",
            "get_leave_balance",
            "get_company_holidays",
            "apply_leave",
            "get_leave_requests"
        }

    def call_ai(self, messages):

        headers = {
            "Authorization": (
                f"Bearer {OPENROUTER_API_KEY}"
            ),
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Task 19 AI Employee Assistant"
        }

        payload = {
            "model": OPENROUTER_MODEL,

            # OpenRouter will automatically use these
            # if the primary model cannot serve the request.
            "models": OPENROUTER_FALLBACK_MODELS,

            "messages": messages,

            "tools": self.get_tools(),

            "tool_choice": "auto",

            "temperature": 0.2
        }

        try:

            response = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

        except requests.RequestException as exc:

            raise RuntimeError(
                f"Unable to connect to OpenRouter: {exc}"
            )

        if response.status_code == 401:

            raise RuntimeError(
                "Invalid OpenRouter API key."
            )

        if response.status_code == 402:

            raise RuntimeError(
                "OpenRouter payment or credit limit reached."
            )

        if response.status_code == 429:

            raise RuntimeError(
                "All configured OpenRouter models "
                "are currently rate limited."
            )

        if response.status_code >= 500:

            raise RuntimeError(
                f"OpenRouter server error: "
                f"{response.status_code}"
            )

        if response.status_code != 200:

            raise RuntimeError(
                f"OpenRouter API error "
                f"{response.status_code}: "
                f"{response.text}"
            )

        try:

            return response.json()

        except ValueError:

            raise RuntimeError(
                "OpenRouter returned invalid JSON."
            )

    def run(
        self,
        session_id: str,
        user_message: str
    ):

        history = get_history(session_id)

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        messages.extend(history)

        messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        tools_used = []

        for _ in range(MAX_TOOL_ROUNDS):

            result = self.call_ai(messages)

            choices = result.get("choices", [])

            if not choices:

                raise RuntimeError(
                    "OpenRouter returned no choices."
                )

            assistant_message = choices[0].get(
                "message",
                {}
            )

            tool_calls = assistant_message.get(
                "tool_calls"
            )

            # No more tools needed.
            if not tool_calls:

                final_response = (
                    assistant_message.get("content")
                )

                if not final_response:

                    raise RuntimeError(
                        "AI returned an empty response."
                    )

                add_message(
                    session_id,
                    {
                        "role": "user",
                        "content": user_message
                    }
                )

                add_message(
                    session_id,
                    {
                        "role": "assistant",
                        "content": final_response
                    }
                )

                return {
                    "response": final_response,
                    "tools_used": tools_used
                }

            # Add assistant tool-call message
            messages.append(assistant_message)

            for tool_call in tool_calls:

                function_data = tool_call.get(
                    "function",
                    {}
                )

                tool_name = function_data.get("name")

                raw_arguments = function_data.get(
                    "arguments",
                    "{}"
                )

                if tool_name not in self.get_tool_names():

                    raise RuntimeError(
                        f"Unknown tool requested: "
                        f"{tool_name}"
                    )

                try:

                    arguments = json.loads(
                        raw_arguments
                    )

                except json.JSONDecodeError:

                    raise RuntimeError(
                        f"Invalid arguments for "
                        f"tool {tool_name}."
                    )

                try:

                    tool_result = execute_tool(
                        tool_name,
                        arguments
                    )

                except Exception as exc:

                    tool_result = {
                        "success": False,
                        "error": str(exc)
                    }

                tools_used.append(tool_name)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "name": tool_name,
                        "content": json.dumps(
                            tool_result,
                            default=str
                        )
                    }
                )

        raise RuntimeError(
            "Maximum tool execution rounds exceeded."
        )