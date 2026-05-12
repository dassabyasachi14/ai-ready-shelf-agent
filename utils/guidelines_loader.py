import json
from pathlib import Path

_DATA = Path(__file__).parent.parent / "data"


def load_brand_guidelines() -> dict:
    with open(_DATA / "brand_guidelines.json", encoding="utf-8") as f:
        return json.load(f)


def load_retailer_rules(retailer: str) -> dict:
    fname = "amazon_rules.json" if retailer == "amazon" else "walmart_rules.json"
    with open(_DATA / fname, encoding="utf-8") as f:
        return json.load(f)


def load_ai_criteria(retailer: str) -> dict:
    fname = "rufus_criteria.json" if retailer == "amazon" else "sparky_criteria.json"
    with open(_DATA / fname, encoding="utf-8") as f:
        return json.load(f)
