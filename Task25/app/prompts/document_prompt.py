
DOCUMENT_PROMPT = """
Analyze this image as a document.

Extract only text and fields that are visibly readable.

Return JSON with:
{
  "analysis_type": "document",
  "description": "string",
  "document_type": "string or null",
  "visible_text": [],
  "objects": [],
  "attributes": {},
  "fields": {},
  "uncertain_details": [],
  "observed": [],
  "not_determinable": []
}

If a field cannot be read, use null or clearly explain
the uncertainty.

Do not invent invoice numbers, dates, totals, names,
addresses, or other document information.
"""