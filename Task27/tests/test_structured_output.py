from app.models.chat import (
    ChatResponse
)


def test_structured_response():

    response = ChatResponse.model_validate(

        {
            "success": True,

            "status_code": 200,

            "conversation_id":
                "conversation-1",

            "answer":
                "Hello",

            "sources": [],

            "tool_calls": [],

            "trace_id":
                "trace-1"
        }
    )

    assert response.success is True