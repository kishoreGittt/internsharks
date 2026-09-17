
PRODUCT_PROMPT = """
Analyze this product image.

Return JSON with:
{
  "analysis_type": "product",
  "description": "string",
  "product_category": "string or null",
  "visible_text": [],
  "objects": [],
  "attributes": {},
  "colors": [],
  "visible_features": [],
  "uncertain_details": [],
  "observed": [],
  "not_determinable": []
}

Only report visible product features.

Do not invent:
- Brand
- Price
- Material
- Internal specifications
- Hidden features
"""