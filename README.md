# 🛡️ Digital Shelf Compliance Copilot

> **Mars Petcare · Dry Dog Food · Amazon & Walmart**

---

## 👥 Team Name
**The Think Crew**

---

## 🎯 Theme Selected
**Agentic for Business**

---

## ❗ Problem Statement

Mars Petcare brand managers manually audit product listings on Amazon and Walmart to check for brand guideline violations, retailer platform rule breaches, and poor AI-discoverability — a process that is slow, inconsistent, and error-prone. As AI shopping assistants like Amazon Rufus and Walmart Sparky increasingly influence purchase decisions, listings that fail AI-readiness criteria lose visibility and sales without the brand team even knowing.

There is no automated tool that simultaneously checks brand compliance, retailer platform rules, and AI-readiness scoring, and then generates corrective content — all in one workflow.

---

## 💡 Solution Overview

**Digital Shelf Compliance Copilot** is an agentic AI system that audits Mars Petcare dry dog food listings on Amazon and Walmart end-to-end in ~30 seconds.

A brand manager selects a SKU and retailer, clicks **Analyze shelf**, and the system automatically:

1. **Scans** the product listing — extracts title, bullets, description, ingredients, and claims from the retailer's HTML page
2. **Audits** the content against three layers of rules in a single Claude API call:
   - Brand guidelines (naming, approved claims, regulatory rules)
   - Retailer platform rules (title length, bullet format, prohibited terms)
   - AI-readiness criteria for Rufus (Amazon) and Sparky (Walmart)
3. **Scores** the listing 0–100 with deduction-based scoring for violations and additive scoring for AI-readiness
4. **Generates** a fully corrective rewrite — a new title, bullets, and description that fixes every violation and satisfies both retailers simultaneously
5. **Delivers** a formatted HTML gap report via email to any recipient

**Score tiers:** `80–100 AI-Ready ✅` · `60–79 Needs Attention 🟡` · `40–59 At Risk 🟠` · `0–39 Critical 🔴`

**SKUs covered:** IAMS ProActive Health MiniChunks · IAMS ProActive Health Large Breed · Pedigree Complete Nutrition
**Retailers:** Amazon · Walmart

---

## 🛠️ Tech Stack Used

| Layer | Technology |
|---|---|
| **AI Orchestration** | LangGraph (sequential 3-node agentic pipeline) |
| **LLM** | Anthropic Claude (`claude-sonnet-4-20250514`) |
| **Web UI** | Streamlit |
| **HTML Parsing** | BeautifulSoup4 + `__NEXT_DATA__` JSON (Walmart) |
| **Email Delivery** | Python smtplib — Gmail SMTP / TLS |
| **Language** | Python 3.11+ |
| **Deployment** | Streamlit Community Cloud |
| **Version Control** | GitHub |

---

## 🏗️ Architecture Summary

```
                    ┌──────────────────────────────────────────────┐
                    │             LangGraph Pipeline               │
                    │                                              │
  HTML Fixture ──►  │  Node 1        Node 2            Node 3     │
  (6 pre-captured   │  Shelf   ───►  Compliance  ───►  Recovery   │
   product pages)   │  Scanner       + AI-Ready        Generator  │
                    │                Agent                         │
                    └──────────────────────────────────────────────┘
                             │              │              │
                         product_data  violations +    recovered
                                        scores         content
                                             │
                                     Streamlit UI
                              (Scorecard · Recovery · Email)
```

### Node 1 — Shelf Scanner
Parses retailer HTML using BeautifulSoup. Extracts title, bullets, description, ingredients, visible claims, image count, and star rating. Handles Walmart (`__NEXT_DATA__` Next.js JSON) and Amazon (CSS selectors) page structures without live scraping.

### Node 2 — Compliance + AI-Readiness Agent
Single Claude API call returning three scored sections:
- **Section A** — Brand compliance vs `brand_guidelines.json` (max 40 pts, deduction-based: Critical −20, High −10, Medium −5)
- **Section B** — Retailer platform rules vs `amazon_rules.json` / `walmart_rules.json` (max 30 pts, deduction-based: Critical −15, High −8, Medium −4)
- **Section C** — AI-readiness vs `rufus_criteria.json` / `sparky_criteria.json` (max 30 pts, additive per dimension)

Each violation includes severity, exact quoted text, rule cited, and points deducted.

### Node 3 — Recovery Generator
Receives violations + original content from Claude, rewrites the title, bullets, and description to fix every violation. Output must satisfy **both** Amazon and Walmart simultaneously. Title written to Walmart's 90-character ideal limit (the more restrictive standard).

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/dassabyasachi14/ai-ready-shelf-agent.git
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
| `ANTHROPIC_API_KEY` | Anthropic API key — get one at [console.anthropic.com](https://console.anthropic.com) |
| `SMTP_HOST` | `smtp.gmail.com` (fixed) |
| `SMTP_PORT` | `587` (fixed) |
| `SMTP_USER` | Your Gmail address |
| `SMTP_PASSWORD` | Gmail App Password — generate at [myaccount.google.com](https://myaccount.google.com) → Security → 2-Step Verification → App passwords |

---

## ▶️ Run Instructions

### 🌐 Live App (Hosted)
The app is deployed and publicly accessible at:

**[https://digital-shelf-agent.streamlit.app/](https://digital-shelf-agent.streamlit.app/)**

No installation required — open the URL and start analysing.

### Using the app
1. Select a **SKU** from the dropdown (IAMS MiniChunks, IAMS Large Breed, or Pedigree Complete Nutrition)
2. Select a **Retailer** (Amazon or Walmart)
3. Click **▶ Analyze shelf**
4. Watch the three agent nodes run live in the **Scorecard** tab
5. View the full compliance score, violations, and AI-readiness breakdown
6. Switch to the **Recovery** tab to see before/after corrective content
7. Use **Email this report** to send the full gap report to any recipient
8. View all past runs in the **Agent Run Logs** tab

### 💻 Run Locally (Optional)
```bash
streamlit run ui/app.py
```
The app opens at **http://localhost:8501**

---

*Developed for the **Tiger Premier League Hackathon** by **The Think Crew** — Mars Petcare, 2025.*
