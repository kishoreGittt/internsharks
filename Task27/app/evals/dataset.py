EVALUATION_DATASET = [

    {
        "id": "rag_correct",
        "category": "rag",
        "description":
            "Correct answer from selected document."
    },

    {
        "id": "missing_information",
        "category": "rag",
        "description":
            "Refuse when information is absent."
    },

    {
        "id": "document_isolation",
        "category": "security",
        "description":
            "User cannot retrieve another user's document."
    },

    {
        "id": "cross_user_isolation",
        "category": "security",
        "description":
            "User A cannot retrieve User B's data."
    },

    {
        "id": "hallucination_check",
        "category": "grounding",
        "description":
            "Do not invent unsupported database information."
    },

    {
        "id": "tool_required",
        "category": "tools",
        "description":
            "Use project tool for current project tasks."
    },

    {
        "id": "tool_not_required",
        "category": "tools",
        "description":
            "Normal explanations should not call tools."
    },

    {
        "id": "invalid_tool_arguments",
        "category": "tools",
        "description":
            "Invalid tool arguments must be rejected."
    },

    {
        "id": "structured_output",
        "category": "validation",
        "description":
            "Final AI response must satisfy Pydantic schema."
    },

    {
        "id": "failure_handling",
        "category": "reliability",
        "description":
            "Failed jobs must become FAILED."
    },

    {
        "id": "vision_grounding",
        "category": "vision",
        "description":
            "Vision must not invent invisible details."
    }
]