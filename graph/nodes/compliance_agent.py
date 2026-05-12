import json
from typing import Any, Dict

import os
import anthropic

from utils.guidelines_loader import load_brand_guidelines, load_retailer_rules, load_ai_criteria
from utils.json_parser import extract_json
from utils.scorer import calculate_scores

MODEL = "claude-sonnet-4-20250514"

_PROMPT = """\
You are a digital shelf compliance expert for Mars Petcare. Analyze the product listing content below against the provided guidelines and return a structured JSON audit.

## Product Content
{product_json}

## Brand Guidelines
{brand_guidelines}

## Retailer Rules ({retailer})
{retailer_rules}

## AI-Readiness Criteria ({ai_assistant})
{ai_criteria}

## Instructions

Analyze the product content thoroughly and return ONLY a JSON object with this exact structure:

{{
  "section_a_violations": [
    {{
      "section": "A",
      "severity": "critical|high|medium",
      "field": "title|bullets|description|ingredients|general",
      "quoted_text": "exact verbatim text from the listing that violates the rule — empty string if no specific quote",
      "rule_id": "rule identifier from brand_guidelines",
      "rule_description": "clear description of the violation",
      "points_deduction": 20
    }}
  ],
  "section_b_violations": [
    {{
      "section": "B",
      "severity": "critical|high|medium",
      "field": "title|bullets|description|general",
      "quoted_text": "exact verbatim text from the listing",
      "rule_id": "rule identifier from retailer rules",
      "rule_description": "clear description of the violation",
      "points_deduction": 15
    }}
  ],
  "section_c_dimensions": {{
    "dimension_id": {{
      "label": "dimension label",
      "score": 0,
      "max_score": 0,
      "rationale": "1-2 sentence explanation of the score awarded"
    }}
  }}
}}

Scoring rules:
- Section A Brand: Critical = 20 pts deduction, High = 10, Medium = 5
- Section B Platform: Critical = 15 pts deduction, High = 8, Medium = 4
- Section C AI-Readiness: additive, score each dimension from 0 to its max_score as defined in the criteria

IMPORTANT:
- Only report violations that you can substantiate from the actual listing content provided
- For quoted_text, always quote the actual problematic text verbatim from the listing
- Section C: score ALL dimensions from the criteria, even those with full marks
- Return ONLY the JSON object, no explanation or markdown
"""


def compliance_agent_node(state: dict) -> dict:
    product_data = state["product_data"]
    retailer = state["retailer"]
    sku_id = state["sku_id"]

    brand_guidelines = load_brand_guidelines()
    retailer_rules = load_retailer_rules(retailer)
    ai_criteria = load_ai_criteria(retailer)

    ai_assistant = "Rufus" if retailer == "amazon" else "Sparky"

    prompt = _PROMPT.format(
        product_json=json.dumps(product_data, indent=2),
        brand_guidelines=json.dumps(brand_guidelines, indent=2),
        retailer=retailer.capitalize(),
        retailer_rules=json.dumps(retailer_rules, indent=2),
        ai_assistant=ai_assistant,
        ai_criteria=json.dumps(ai_criteria, indent=2),
    )

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text
    parsed = extract_json(raw)

    if not parsed:
        return {
            "violations": [],
            "ai_dimensions": {},
            "scores": calculate_scores([], {}),
            "errors": state.get("errors", []) + ["compliance_agent: failed to parse LLM response"],
        }

    section_a = parsed.get("section_a_violations", [])
    section_b = parsed.get("section_b_violations", [])
    violations = section_a + section_b

    raw_dims = parsed.get("section_c_dimensions", {})
    # Normalise dimension scores from raw (out of max per dimension) to proportional
    ai_dimensions: Dict[str, Any] = {}
    for dim_id, dim_data in raw_dims.items():
        ai_dimensions[dim_id] = {
            "label": dim_data.get("label", dim_id),
            "score": int(dim_data.get("score", 0)),
            "max_score": int(dim_data.get("max_score", 0)),
            "rationale": dim_data.get("rationale", ""),
        }

    scores = calculate_scores(violations, ai_dimensions)

    return {
        "violations": violations,
        "ai_dimensions": ai_dimensions,
        "scores": scores,
    }
