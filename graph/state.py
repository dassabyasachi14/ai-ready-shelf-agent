from typing import Any, Dict, List, Optional, TypedDict


class DigitalShelfState(TypedDict, total=False):
    # Inputs
    sku_id: str
    retailer: str

    # Node 1 — Shelf Scanner
    product_data: Optional[Dict[str, Any]]
    raw_html: Optional[str]

    # Node 2 — Compliance + AI-Readiness
    violations: Optional[List[Dict[str, Any]]]
    ai_dimensions: Optional[Dict[str, Dict[str, Any]]]
    scores: Optional[Dict[str, Any]]

    # Node 3 — Recovery Generator
    recovered: Optional[Dict[str, Any]]

    # Progress
    node_statuses: Optional[Dict[str, str]]
    errors: Optional[List[str]]
