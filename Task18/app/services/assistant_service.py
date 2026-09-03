import json

from google.genai import types

from app.services.ai_service import AIService
from app.models.assistant import (
    CalculatorArguments,
    GetTaskArguments
)
from app.tools.registry import (
    TOOL_REGISTRY,
    get_registered_tool
)
from app.prompts.assistant_prompt import SYSTEM_PROMPT


class AssistantService:

    def __init__(self):
        self.ai_service = AIService()

    def get_tool_declarations(self):

        calculator_tool = types.FunctionDeclaration(
            name="calculator",
            description=(
                "Perform arithmetic calculations. "
                "Use for addition, subtraction, "
                "multiplication, and division."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Operation: add, subtract, "
                            "multiply, or divide"
                        )
                    },
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": [
                    "operation",
                    "a",
                    "b"
                ]
            }
        )

        date_tool = types.FunctionDeclaration(
            name="get_current_date",
            description=(
                "Get the current date."
            ),
            parameters={
                "type": "object",
                "properties": {}
            }
        )

        task_tool = types.FunctionDeclaration(
            name="get_task",
            description=(
                "Get information and status "
                "of a task using its task ID."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "Task ID"
                    }
                },
                "required": [
                    "task_id"
                ]
            }
        )

        return types.Tool(
            function_declarations=[
                calculator_tool,
                date_tool,
                task_tool
            ]
        )

    def validate_and_execute(
        self,
        tool_name: str,
        arguments: dict
    ):

        # Security check
        if tool_name not in TOOL_REGISTRY:
            raise ValueError(
                f"Tool '{tool_name}' is not registered."
            )

        tool = get_registered_tool(tool_name)

        if tool_name == "calculator":

            validated = CalculatorArguments(
                **arguments
            )

            return tool(
                operation=validated.operation,
                a=validated.a,
                b=validated.b
            )

        elif tool_name == "get_current_date":

            return tool()

        elif tool_name == "get_task":

            validated = GetTaskArguments(
                **arguments
            )

            return tool(
                task_id=validated.task_id
            )

        raise ValueError(
            f"Unsupported tool: {tool_name}"
        )

    def process_message(self, message: str):

        tool = self.get_tool_declarations()

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=(
                            SYSTEM_PROMPT
                            + "\n\nUser message:\n"
                            + message
                        )
                    )
                ]
            )
        ]

        # First Gemini call
        response = self.ai_service.generate_response(
            contents=contents,
            tools=[tool]
        )

        candidate = response.candidates[0]

        function_calls = []

        for part in candidate.content.parts:

            if part.function_call:
                function_calls.append(
                    part.function_call
                )

        # No tool required
        if not function_calls:

            return {
                "response": response.text,
                "tool_used": None
            }

        # Add Gemini response to conversation
        contents.append(
            candidate.content
        )

        tool_used = []

        # Execute requested tools
        for function_call in function_calls:

            tool_name = function_call.name

            arguments = dict(
                function_call.args
            )

            try:

                result = self.validate_and_execute(
                    tool_name,
                    arguments
                )

            except Exception as exc:

                result = {
                    "error": str(exc)
                }

            tool_used.append(tool_name)

            # Send function result back to Gemini
            function_response_part = (
                types.Part.from_function_response(
                    name=tool_name,
                    response={
                        "result": result
                    }
                )
            )

            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        function_response_part
                    ]
                )
            )

        # Second Gemini call
        final_response = (
            self.ai_service.generate_response(
                contents=contents
            )
        )

        return {
            "response": final_response.text,
            "tool_used": tool_used
        }