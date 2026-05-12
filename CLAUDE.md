# CLAUDE.md — AI-Ready Digital Shelf Agent

## Project Overview
An agentic AI system that monitors Mars Petcare dry dog food listings on Amazon and Walmart,
detects brand guideline and retailer platform violations, scores AI discoverability for Rufus
and Sparky, generates compliant corrective content, and delivers results via email.

**Stack:** Python 3.11 · LangGraph · Anthropic Claude API · Streamlit
**Model:** `claude-sonnet-4-20250514` for all LLM calls

---

## Directory Structure

```
ai_ready_shelf_agent/
├── data/
│   ├── html_fixtures/          # 6 static HTML pages — 3 SKUs × 2 retailers
│   ├── brand_guidelines.json
│   ├── amazon_rules.json
│   ├── walmart_rules.json
│   ├── rufus_criteria.json
│   └── sparky_criteria.json
├── graph/
│   ├── state.py                # DigitalShelfState TypedDict
│   ├── graph.py                # LangGraph compile
│   └── nodes/
│       ├── shelf_scanner.py    # Node 1 — extract content from HTML
│       ├── compliance_agent.py # Node 2 — compliance + AI-readiness
│       └── recovery_generator.py # Node 3 — rewrite corrective content
├── utils/
│   ├── html_loader.py          # Load fixture by (sku, retailer) key
│   ├── guidelines_loader.py    # Load correct JSON set per retailer
│   ├── json_parser.py          # Safe JSON extraction from LLM output
│   ├── scorer.py               # Score calculation and tier labelling
│   └── email_sender.py         # Compile and send HTML email report
├── ui/
│   └── app.py                  # Streamlit application
├── GUIDELINES.md               # All guidelines JSON data — copy into data/
├── PRODUCTS.md                 # SKU URLs, expected scores for testing
├── PITCH.md                    # Demo script — not for build
├── .env
└── requirements.txt
```

---

## How to Run

```bash
pip install -r requirements.txt
streamlit run ui/app.py
```

---

## Architecture

Three LangGraph nodes run sequentially per SKU × retailer selection:

1. **Shelf Scanner** — reads static HTML fixture, extracts structured product data
   (title, bullets, description, ingredients, visible claims, image count, rating)

2. **Compliance + AI-Readiness Agent** — single Claude call, two outputs:
   - Section A: Brand compliance against `brand_guidelines.json` (max 40 pts)
   - Section B: Retailer platform rules against `amazon_rules.json` or `walmart_rules.json` (max 30 pts)
   - Section C: AI-readiness against `rufus_criteria.json` or `sparky_criteria.json` (max 30 pts)
   Returns violations with severity, exact quoted text, rule cited, and points impact.

3. **Recovery Generator** — receives violations and original content, rewrites title,
   bullets, and description to fix all violations. Content must satisfy both Amazon
   and Walmart simultaneously. Includes change notes per fix.

Graph: `START → shelf_scanner → compliance_agent → recovery_generator → END`

---

## Key Constraints — Read Before Writing Any Code

- **Static HTML only.** No live scraping. All 6 fixtures are pre-captured files in `data/html_fixtures/`.
- **Retailer guidelines are injected as parameters.** The compliance agent runs once
  with either Amazon or Walmart guidelines — not both at once.
- **Agent discovers violations from HTML.** Do not hardcode expected violations.
  The agent reads real content and reasons against the guidelines JSON.
- **Recovery must satisfy both retailers.** Write recovered title to Walmart's
  90-character ideal limit (the more restrictive of the two).
- **No pre-loaded results.** The UI only shows results from live runs in the current session.
- **Progressive output.** Stream each node's findings to the UI as it completes.
  Do not wait for all nodes to finish before showing results.
- **Scoring is deduction-based for A and B, additive for C.**
  Scores floor at 0 — cannot go negative.

---

## Scoring Model

| Section | Max | Model |
|---|---|---|
| A — Brand Compliance | 40 | Deductions: Critical −20, High −10, Medium −5 |
| B — Platform Rules | 30 | Deductions: Critical −15, High −8, Medium −4 |
| C — AI-Readiness | 30 | Additive: award points per dimension (see guidelines JSON) |
| **Total** | **100** | |

Score tiers: 80–100 AI-Ready ✅ · 60–79 Needs Attention 🟡 · 40–59 At Risk 🟠 · 0–39 Critical 🔴

---

## UI Specification

**Controls:** SKU dropdown + Retailer dropdown + Analyze button
- SKUs: `iams_minichunks` · `iams_largebreed` · `pedigree_compnutr`
- Retailers: `amazon` · `walmart`

**Live output panel:** Updates progressively as each node completes.
Show node name, status, and key findings as they stream in.

**Results layout (two columns):**
- Left: Compliance scorecard (Brand + Platform) with `st.progress()` bars and violations list
- Right: AI-Readiness scorecard with dimension-level breakdown

**Violations detail:** Top 3 expanded by default, rest in expander.
Each violation shows: severity badge, field, exact quoted text, rule violated, points impact.

**Recovery content:** Before/After comparison for title. Expandable sections for bullets and description.

**Email report:** Text input for email address + Send button. Compile full report as HTML email via SMTP.

**Previous Results:** Table at bottom of page. Populated from `st.session_state["results_history"]` 
during current session only. Nothing pre-loaded. [View] button recalls a past result.

---

## Data Files

All guidelines JSON is in `GUIDELINES.md`. Copy each block into the corresponding file in `data/`
before running. Five files: `brand_guidelines.json`, `amazon_rules.json`, `walmart_rules.json`,
`rufus_criteria.json`, `sparky_criteria.json`.

Product page URLs and expected score ranges for testing are in `PRODUCTS.md`.

---

## SKU and Retailer Mapping

```
iams_minichunks   → IAMS ProActive Health Adult MiniChunks Chicken 30lb
iams_largebreed   → IAMS ProActive Health Large Breed Adult Chicken 30lb
pedigree_compnutr → Pedigree Complete Nutrition Adult Roasted Chicken 30lb

amazon  → uses amazon_rules.json + rufus_criteria.json
walmart → uses walmart_rules.json + sparky_criteria.json
```

HTML fixture filenames: `{sku_id}_{retailer}.html`
Example: `data/html_fixtures/pedigree_compnutr_walmart.html`

---

## Environment Variables

```
ANTHROPIC_API_KEY=
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

---

## Dependencies

```
anthropic>=0.25.0
langgraph>=0.1.0
streamlit>=1.35.0
python-dotenv>=1.0.0
beautifulsoup4>=4.12.0
plotly>=5.18.0
```
