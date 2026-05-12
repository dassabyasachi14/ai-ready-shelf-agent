import json
import re
from html import unescape
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from utils.html_loader import load_fixture


# ── Walmart ──────────────────────────────────────────────────────────────────

def _find_key_recursive(data: Any, key: str, depth: int = 0) -> Any:
    """Recursively search a nested dict/list for a key."""
    if depth > 10:
        return None
    if isinstance(data, dict):
        if key in data and data[key]:
            return data[key]
        for v in data.values():
            result = _find_key_recursive(v, key, depth + 1)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = _find_key_recursive(item, key, depth + 1)
            if result:
                return result
    return None


def _parse_walmart(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    # Walmart embeds all product data in __NEXT_DATA__ script tag
    next_data: dict = {}
    next_data_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if next_data_tag and next_data_tag.string:
        try:
            next_data = json.loads(next_data_tag.string)
        except (json.JSONDecodeError, AttributeError):
            pass

    # Use <title> tag — contains actual listing title with any capitalisation violations intact
    title = ""
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(strip=True)
    # Fall back to og:title
    if not title:
        og = soup.find("meta", property="og:title")
        if og:
            title = og.get("content", "")
    title = re.sub(r"\s*-\s*Walmart\.com\s*$", "", title).strip()

    # Extract description from shortDescription
    description = ""
    raw_short = _find_key_recursive(next_data, "shortDescription") if next_data else ""
    if raw_short and isinstance(raw_short, str):
        description = BeautifulSoup(unescape(raw_short), "html.parser").get_text(" ", strip=True)
    if not description:
        og_desc = soup.find("meta", {"name": "description"})
        if og_desc:
            description = og_desc.get("content", "")

    # Extract bullets from longDescription HTML
    bullets: List[str] = []
    raw_long = _find_key_recursive(next_data, "longDescription") if next_data else ""
    if raw_long and isinstance(raw_long, str):
        long_soup = BeautifulSoup(unescape(raw_long), "html.parser")
        bullets = [li.get_text(strip=True) for li in long_soup.find_all("li") if li.get_text(strip=True)]

    # Fallback: highlights array
    if not bullets and next_data:
        highlights = _find_key_recursive(next_data, "highlights") or []
        if isinstance(highlights, list):
            bullets = [h if isinstance(h, str) else h.get("value", "") for h in highlights if h]

    # Extract rating
    rating = None
    if next_data:
        avg = _find_key_recursive(next_data, "averageRating")
        if avg:
            try:
                rating = float(avg)
            except (TypeError, ValueError):
                pass
    if not rating:
        rating_match = re.search(r'"averageRating":([0-9.]+)', html)
        rating = float(rating_match.group(1)) if rating_match else None

    # Image count
    image_count = len(re.findall(r'"imageInfo":\{', html))
    if image_count == 0:
        image_count = 3  # conservative default

    # Extract ingredients
    ingredients = _extract_ingredients_text(html, soup)

    # Visible claims
    visible_claims = _extract_visible_claims(bullets, description, title)

    return {
        "title": title,
        "bullets": bullets,
        "description": description,
        "ingredients": ingredients,
        "visible_claims": visible_claims,
        "image_count": max(1, min(image_count, 15)),
        "rating": rating,
    }


# ── Amazon ────────────────────────────────────────────────────────────────────

def _parse_amazon(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title = ""
    title_el = soup.find(id="productTitle")
    if title_el:
        title = title_el.get_text(strip=True)

    # Bullets
    bullets: List[str] = []
    bullets_el = soup.find(id="feature-bullets") or soup.find(id="featurebullets_feature_div")
    if bullets_el:
        items = bullets_el.find_all("span", class_="a-list-item")
        bullets = [it.get_text(strip=True) for it in items if it.get_text(strip=True)]

    # Description
    description = ""
    desc_el = soup.find(id="productDescription")
    if desc_el:
        description = desc_el.get_text(" ", strip=True)
    if not description:
        aplus = soup.find(id="aplus") or soup.find(id="aplusBrandStory_feature_div")
        if aplus:
            description = aplus.get_text(" ", strip=True)[:2000]

    # Rating
    rating = None
    rating_el = soup.find(id="acrPopover")
    if rating_el:
        title_attr = rating_el.get("title", "")
        m = re.search(r"([0-9.]+)", title_attr)
        if m:
            rating = float(m.group(1))
    if not rating:
        m = re.search(r'"ratingScore":"([0-9.]+)"', html)
        if m:
            rating = float(m.group(1))

    # Image count
    alt_imgs = soup.find(id="altImages")
    if alt_imgs:
        image_count = len(alt_imgs.find_all("img"))
    else:
        image_count = len(soup.find_all("img", id=re.compile(r"main-image|product-image", re.I)))
    image_count = max(1, min(image_count, 15))

    # Ingredients
    ingredients = _extract_ingredients_text(html, soup)

    # Visible claims
    visible_claims = _extract_visible_claims(bullets, description, title)

    return {
        "title": title,
        "bullets": bullets,
        "description": description,
        "ingredients": ingredients,
        "visible_claims": visible_claims,
        "image_count": image_count,
        "rating": rating,
    }


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _extract_ingredients_text(html: str, soup: BeautifulSoup) -> str:
    # Amazon: ingredients expander section
    ing_el = soup.find(id="ingredients-expander") or soup.find(id="ingredient-section")
    if ing_el:
        return ing_el.get_text(" ", strip=True)[:1000]

    # General: look for text following "Ingredients:" pattern in the raw HTML
    m = re.search(r"Ingredients\s*:?\s*([A-Z][^<]{40,600})", html, re.IGNORECASE)
    if m:
        return m.group(0)[:600]

    # Walmart: product.ingredientList or similar
    m2 = re.search(r'"ingredients?(?:List)?"\s*:\s*"([^"]{30,600})"', html, re.IGNORECASE)
    if m2:
        return unescape(m2.group(1))

    return ""


def _extract_visible_claims(bullets: List[str], description: str, title: str) -> List[str]:
    all_text = " ".join([title] + bullets + [description]).lower()
    claim_patterns = [
        ("Made in USA", r"\bmade in (?:the )?usa\b"),
        ("Domestically crafted", r"domestically crafted"),
        ("World's Finest", r"world.s finest"),
        ("Natural", r"\bnatural\b"),
        ("No artificial", r"no artificial"),
        ("AAFCO", r"\baafco\b"),
        ("Vet recommended", r"vet(?:erinarian)?s?\s+recommend"),
        ("100% complete", r"100%?\s+complete"),
        ("No fillers", r"no fillers"),
        ("BHA", r"\bbha\b"),
        ("Grain-free", r"grain.free"),
    ]
    found = []
    for label, pattern in claim_patterns:
        if re.search(pattern, all_text, re.IGNORECASE):
            found.append(label)
    return found


# ── Node entry point ──────────────────────────────────────────────────────────

def shelf_scanner_node(state: dict) -> dict:
    sku_id = state["sku_id"]
    retailer = state["retailer"]

    html = load_fixture(sku_id, retailer)

    if retailer == "walmart":
        product_data = _parse_walmart(html)
    else:
        product_data = _parse_amazon(html)

    product_data["sku_id"] = sku_id
    product_data["retailer"] = retailer

    return {
        "product_data": product_data,
        "raw_html": "",  # don't carry the full HTML into state
    }
