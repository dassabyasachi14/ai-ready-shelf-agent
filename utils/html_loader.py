from pathlib import Path


def load_fixture(sku_id: str, retailer: str) -> str:
    path = Path(__file__).parent.parent / "data" / "html_fixtures" / f"{sku_id}_{retailer}.html"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
