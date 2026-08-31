def create_summarization_prompt(
    text: str,
    summary_type: str
) -> str:

    if summary_type == "brief":

        instruction = """
Create a short summary in 2 to 4 sentences.
Focus only on the most important information.
"""

    elif summary_type == "detailed":

        instruction = """
Create a detailed summary.
Include the important ideas, facts, requirements,
and conclusions from the text.
"""

    elif summary_type == "bullet_points":

        instruction = """
Create the summary using clear bullet points.
Include the most important information from the text.
"""

    else:

        raise ValueError("Invalid summary type")

    return f"""
You are an AI document summarization assistant.

Read the following text and create a useful summary.

Summary type:
{summary_type}

Instructions:
{instruction}

Also identify:

1. Main topic
2. Important keywords

Return ONLY valid JSON.

Use exactly this structure:

{{
    "summary": "summary here",
    "main_topic": "main topic here",
    "keywords": [
        "keyword1",
        "keyword2",
        "keyword3"
    ]
}}

Do not return Markdown.
Do not return ```json.
Do not add any explanation outside the JSON.

Document text:

{text}
"""