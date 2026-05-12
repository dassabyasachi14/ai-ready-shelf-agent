# 🛡️ AI-Ready Digital Shelf Agent

> **Mars Petcare · Dry Dog Food · Amazon & Walmart**
> 
> An agentic AI system that monitors product listings, detects brand and retailer compliance violations, scores AI discoverability for Amazon Rufus and Walmart Sparky, generates compliant corrective content, and delivers a full gap report via email.

---

## 📸 Overview

The AI-Ready Digital Shelf Agent automates the manual process of auditing product content on major retail platforms. A brand manager selects a SKU and retailer, clicks **Analyze shelf**, and within ~30 seconds receives:

- A **compliance score** (0–100) broken down across Brand Guidelines, Platform Rules, and AI-Readiness
- A **violations list** with exact quoted text, the rule violated, and points deducted
- **Recovered content** — an AI-rewritten title, bullet points, and description that fixes every violation
- A **formatted HTML email report** sent directly to any recipient

---

## 🏗️ Architecture

```
                         ┌─────────────────────────────────────────────┐
                         │              LangGraph Pipeline              │
                         │                                              │
  HTML Fixture  ──────►  │  Node 1          Node 2            Node 3   │
  (6 pre-captured        │  Shelf     ───►  Compliance  ───►  Recovery  │
   product pages)        │  Scanner         + AI-Ready        Generator │
                         │                  Agent                       │
                         └─────────────────────────────────────────────┘
                                  │               │              │
                              product_data   violations      recovered
                                             + scores         content
                                                  │
                                          Streamlit UI
                                    (Scorecard / Recovery / Email)
```

### Node 1 — Shelf Scanner
Parses static HTML fixtures using BeautifulSoup. Extracts:
- Title, bullet points, description, ingredients
- Visible claims, image count, star rating
- Handles both Walmart (`__NEXT_DATA__` JSON) and Amazon (CSS selectors) page structures

### Node 2 — Compliance + AI-Readiness Agent
Single Claude API call with three output sections:
- **Section A** — Brand compliance vs `brand_guidelines.json` (max 40 pts, deduction-based)
- **Section B** — Retailer platform rules vs `amazon_rules.json` / `walmart_rules.json` (max 30 pts)
- **Section C** — AI-readiness vs `rufus_criteria.json` / `sparky_criteria.json` (max 30 pts, additive)

Returns violations with severity, exact quoted text, rule cited, and points impact.

### Node 3 — Recovery Generator
Receives violations + original content, rewrites title / bullets / description to fix every violation. Content must satisfy **both** Amazon and Walmart simultaneously. Title written to Walmart's 90-character ideal (the more restrictive limit).

---

## 📊 Scoring Model

| Section | Max | Method |
|---|---|---|
| A — Brand Compliance | 40 | Deductions: Critical −20, High −10, Medium −5 |
| B — Platform Rules | 30 | Deductions: Critical −15, High −8, Medium −4 |
| C — AI-Readiness | 30 | Additive: score each dimension, scale to 30 |
| **Total** | **100** | |

**Score tiers:** `80–100 AI-Ready ✅` · `60–79 Needs Attention 🟡` · `40–59 At Risk 🟠` · `0–39 Critical 🔴`

---

## 📁 Project Structure

```
├── data/
│   ├── html_fixtures/          # 6 pre-captured product pages (3 SKUs × 2 retailers)
│   │   ├── iams_minichunks_amazon.html
│   │   ├── iams_minichunks_walmart.html
│   │   ├── iams_largebreed_amazon.html
│   │   ├── iams_largebreed_walmart.html
│   │   ├── pedigree_compnutr_amazon.html
│   │   └── pedigree_compnutr_walmart.html
│   ├── Mars_Logo/
│   │   └── Mars_Petcare_Logo.jpg
│   ├── brand_guidelines.json   # Brand naming, approved claims, regulatory rules
│   ├── amazon_rules.json       # Amazon title/bullet/description platform rules
│   ├── walmart_rules.json      # Walmart title/bullet/description platform rules
│   ├── rufus_criteria.json     # Amazon Rufus AI-readiness scoring dimensions
│   └── sparky_criteria.json    # Walmart Sparky AI-readiness scoring dimensions
│
├── graph/
│   ├── state.py                # DigitalShelfState TypedDict
│   ├── graph.py                # LangGraph compile (START → scanner → compliance → recovery → END)
│   └── nodes/
│       ├── shelf_scanner.py    # HTML parsing (BeautifulSoup + __NEXT_DATA__ JSON)
│       ├── compliance_agent.py # Claude API call → violations + AI-readiness scores
│       └── recovery_generator.py # Claude API call → rewritten compliant content
│
├── utils/
│   ├── html_loader.py          # Load fixture by (sku_id, retailer) key
│   ├── guidelines_loader.py    # Load correct JSON set per retailer
│   ├── json_parser.py          # Safe JSON extraction from LLM output
│   ├── scorer.py               # Score calculation and tier labelling
│   └── email_sender.py         # Compile and send HTML email report via SMTP
│
├── ui/
│   └── app.py                  # Streamlit application (3 tabs: Scorecard, Recovery, Agent Run Logs)
│
├── .streamlit/
│   └── config.toml             # Light theme, primaryColor, font
│
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 🗂️ SKU & Retailer Mapping

| SKU ID | Product | Retailer Rules | AI Assistant |
|---|---|---|---|
| `iams_minichunks` | IAMS ProActive Health Adult MiniChunks Chicken 30lb | `amazon_rules.json` | Rufus |
| `iams_minichunks` | IAMS ProActive Health Adult MiniChunks Chicken 30lb | `walmart_rules.json` | Sparky |
| `iams_largebreed` | IAMS ProActive Health Large Breed Adult Chicken 30lb | `amazon_rules.json` | Rufus |
| `iams_largebreed` | IAMS ProActive Health Large Breed Adult Chicken 30lb | `walmart_rules.json` | Sparky |
| `pedigree_compnutr` | Pedigree Complete Nutrition Adult Roasted Chicken 30lb | `amazon_rules.json` | Rufus |
| `pedigree_compnutr` | Pedigree Complete Nutrition Adult Roasted Chicken 30lb | `walmart_rules.json` | Sparky |

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **AI Orchestration** | LangGraph (sequential 3-node graph) |
| **LLM** | Anthropic Claude (`claude-sonnet-4-20250514`) |
| **Web UI** | Streamlit 1.35+ |
| **HTML Parsing** | BeautifulSoup4 |
| **Email** | Python smtplib (Gmail SMTP / TLS) |
| **Language** | Python 3.11+ |

---

## 🚀 Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-ready-shelf-agent.git
cd ai-ready-shelf-agent
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Open `.env` and fill in your values:

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key — get one at [console.anthropic.com](https://console.anthropic.com) |
| `SMTP_HOST` | `smtp.gmail.com` (fixed) |
| `SMTP_PORT` | `587` (fixed) |
| `SMTP_USER` | Your Gmail address |
| `SMTP_PASSWORD` | A **Gmail App Password** (NOT your regular password) — generate at [myaccount.google.com](https://myaccount.google.com) → Security → 2-Step Verification → App passwords |

### 5. Run the app
```bash
streamlit run ui/app.py
```

The app will open at **http://localhost:8501**

---

## ☁️ Cloud Deployment — Streamlit Community Cloud

> **Why not Vercel?** Vercel is a serverless platform. Streamlit requires a persistent WebSocket server and long-running processes — architecturally incompatible with serverless. **Streamlit Community Cloud** is the correct free platform for Streamlit apps.

### Step-by-step

1. **Push this repo to GitHub** (public or private)

2. **Go to [share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub

3. Click **"New app"** → select your repository → set:
   - **Main file path:** `ui/app.py`
   - **Python version:** 3.11

4. Click **"Advanced settings"** → add your **Secrets** (equivalent to `.env`):
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-api03-..."
   SMTP_HOST = "smtp.gmail.com"
   SMTP_PORT = "587"
   SMTP_USER = "your-email@gmail.com"
   SMTP_PASSWORD = "xxxx xxxx xxxx xxxx"
   ```

5. Click **"Deploy"** — the app will be live at a public URL in ~2 minutes

> **Note:** Streamlit Community Cloud reads secrets from the Secrets panel, NOT from `.env` files. The `load_dotenv()` calls in the code gracefully fall back to `os.environ`, which Streamlit Cloud populates from its secrets panel automatically.

---

## 📧 Email Report

The app sends a fully-formatted HTML email report containing:
- Overall compliance score and tier
- Complete violations list with severity, quoted text, and rule references
- Side-by-side before/after for title, bullets, and description
- Change notes explaining each fix

To use this feature, configure Gmail SMTP credentials in `.env` and use the **"Email this report"** section in the Recovery tab.

---

## 🔑 Guidelines Data Sources

| File | Source |
|---|---|
| `brand_guidelines.json` | Inferred from iams.com, pedigree.com, AAFCO, FTC guidelines |
| `amazon_rules.json` | Amazon Seller Central G200390640 + January 2025 title policy |
| `walmart_rules.json` | Official Walmart retailer content guidelines (Mars Petcare team) |
| `rufus_criteria.json` | Amazon Rufus documented behaviour (genrise.ai, pacvue.com) |
| `sparky_criteria.json` | Walmart Sparky documented behaviour (envisionhorizons.com, code3.com) |

---

## 📝 License

This project was developed for the **Tiger Premier League Hackathon** by Mars Petcare. Internal use only.
