def build_document_prompt(
    analysis_type: str,
    document_text: str,
) -> str:
    base_instruction = """
You are a document analysis assistant.

Analyze the document provided below.

Use only information from the document.
Do not invent facts.
Return valid JSON only.
Do not include Markdown code fences.
"""

    if analysis_type == "summary":
        output_instruction = """
Return exactly this JSON structure:

{
  "summary": "A clear summary of the document"
}
"""

    elif analysis_type == "key_points":
        output_instruction = """
Return exactly this JSON structure:

{
  "key_points": [
    "Important point 1",
    "Important point 2",
    "Important point 3"
  ]
}
"""

    elif analysis_type == "document_analysis":
        output_instruction = """
Return exactly this JSON structure:

{
  "title": "Document title",
  "summary": "Document summary",
  "main_topics": [
    "Topic 1",
    "Topic 2"
  ],
  "key_points": [
    "Important point 1",
    "Important point 2"
  ]
}
"""

    else:
        raise ValueError("Unsupported analysis type")

    return f"""
{base_instruction}

{output_instruction}

DOCUMENT:

{document_text}
"""