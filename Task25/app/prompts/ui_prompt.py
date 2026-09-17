
UI_PROMPT = """
Analyze this UI screenshot.

Return JSON with:
{
  "analysis_type": "ui",
  "description": "string",
  "screen_type": "string or null",
  "components": [],
  "buttons": [],
  "input_fields": [],
  "navigation_elements": [],
  "visible_text": [],
  "usability_observations": [],
  "uncertain_details": [],
  "observed": [],
  "not_determinable": []
}

Identify only visible UI elements.

Do not invent backend functionality, hidden interactions,
or implementation details.
"""