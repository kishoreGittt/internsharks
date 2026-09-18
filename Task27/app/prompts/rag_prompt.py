RAG_PROMPT = """
Answer the user's question using only the selected document context.

Selected document context:

{context}

Rules:

- Do not use outside knowledge for document-specific claims.
- Do not invent missing information.
- If the answer cannot be found in the selected documents, respond exactly:

The information was not found in the selected documents.

- Mention document and chunk sources when appropriate.
"""