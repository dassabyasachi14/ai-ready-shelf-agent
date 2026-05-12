import json
import os

import anthropic
from dotenv import load_dotenv

from utils.guidelines_loader import load_brand_guidelines, load_retailer_rules
from utils.json_parser import extract_json

load_dotenv()

MODEL = "claude-sonnet-4-20250514"

_PROMPT = """\
You are a brand-compliant content writer for Mars Petcare. Your task is to rewrite the product listing content to fix ALL compliance violations while preserving the product's genuine benefits.

## Original Product Content
{product_json}

## Violations to Fix
{violations_json}

## Brand Guidelines
{brand_guidelines}

## Amazon Rules (for reference)
{amazon_rules}

## Walmart Rules (primary standard — more restrictive)
{walmart_rules}

## Recovery Requirements

1. **Title**: Maximum 90 characters (Walmart's ideal limit — the more restrictive standard). Must include brand name, product form, flavor, life stage, and size.
2. **Bullets**: 5–6 bullets. Must comply with BOTH Amazon and Walmart rules simultaneously. Start each with a capital letter. No ending punctuation. No prohibited terms.
3. **Description**: 150+ words. Plain prose (no bullets). Compliant with both retailers. Repeat key product attributes for SEO.
4. **Fix every violation** listed — check each one explicitly.
5. **Preserve approved claims** from brand guidelines where they are accurate.

Return ONLY a JSON object with this structure:
{{
  "recovered_title": "...",
  "recovered_bullets": ["bullet 1", "bullet 2", "bullet 3", "bullet 4", "bullet 5"],
  "recovered_description": "...",
  "change_notes": [
    {{
      "type": "removed|added|modified",
      "description": "what was changed and why it fixes a violation",
      "fix_for_rule": "rule_id"
    }}
  ]
}}

Return ONLY the JSON object, no explanation or markdown.
"""


def recovery_generator_node(state: dict) -> dict:
    product_data = state["product_data"]
    violations = state.get("violations", [])

    brand_guidelines = load_brand_guidelines()
    amazon_rules = load_retailer_rules("amazon")
    walmart_rules = load_retailer_rules("walmart")

    prompt = _PROMPT.format(
        product_json=json.dumps(product_data, indent=2),
        violations_json=json.dumps(violations, indent=2),
        brand_guidelines=json.dumps(brand_guidelines, indent=2),
        amazon_rules=json.dumps(amazon_rules, indent=2),
        walmart_rules=json.dumps(walmart_rules, indent=2),
    )

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text
    parsed = extract_json(raw)

    if not parsed:
        return {
            "recovered": {
                "recovered_title": product_data.get("title", ""),
                "recovered_bullets": product_data.get("bullets", []),
                "recovered_description": product_data.get("description", ""),
                "change_notes": [],
            },
            "errors": state.get("errors", []) + ["recovery_generator: failed to parse LLM response"],
        }

    return {
        "recovered": {
            "recovered_title": parsed.get("recovered_title", ""),
            "recovered_bullets": parsed.get("recovered_bullets", []),
            "recovered_description": parsed.get("recovered_description", ""),
            "change_notes": parsed.get("change_notes", []),
        }
    }
