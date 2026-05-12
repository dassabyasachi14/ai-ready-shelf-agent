import sys
import os
import time
import html as _html
from pathlib import Path
from datetime import datetime

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv

# ── Secrets loading ──────────────────────────────────────────────────────────
# Priority: Streamlit Cloud st.secrets → local .env file → existing os.environ

_SECRET_KEYS = [
    "ANTHROPIC_API_KEY",
    "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD",
]

# 1. Streamlit Cloud: read each key from st.secrets into os.environ
for _k in _SECRET_KEYS:
    try:
        _v = st.secrets[_k]
        if _v:
            os.environ[_k] = str(_v)
    except Exception:
        pass

# 2. Local development: fill any remaining keys from .env file
load_dotenv(Path(__file__).parent.parent / ".env", override=False)

from graph.graph import compiled_graph

# ── Mars Petcare logo (base64-embedded so it works inside st.markdown HTML) ──
import base64 as _b64
_logo_path = Path(__file__).parent.parent / "data" / "Mars_Logo" / "Mars_Petcare_Logo.jpg"
_logo_b64  = _b64.b64encode(_logo_path.read_bytes()).decode()
_LOGO_SRC  = f"data:image/jpeg;base64,{_logo_b64}"
from utils.email_sender import send_report


def _md(html: str, **kwargs) -> None:
    """Strip leading whitespace from every line before rendering.
    Prevents Streamlit's Markdown parser from treating 4-space-indented
    lines as code blocks inside unsafe_allow_html HTML strings."""
    cleaned = "\n".join(line.lstrip() for line in html.splitlines()).strip()
    st.markdown(cleaned, unsafe_allow_html=True, **kwargs)

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI-Ready Digital Shelf Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

/* ════════════════════════════════════════════════════
   DESIGN TOKENS — Enterprise SaaS palette
   Primary:  #1E40AF  (deep navy-blue)
   Gold:     #D97706  (Pedigree amber — accent only, never bg)
   Page bg:  #F1F5F9  (slate-50)
   Card bg:  #FFFFFF  (white) / #F8FAFC (alt)
════════════════════════════════════════════════════ */

/* ── Page canvas ── */
html, body { background-color: #F1F5F9 !important; color: #0F172A !important; }
.stApp, section[data-testid="stAppViewContainer"],
section[data-testid="stMain"], .main,
[data-baseweb="tab-panel"], .block-container {
  background-color: #F1F5F9 !important;
}

/* ── Global typography ── */
html, body, .stApp, .stMarkdown, p, span, div, label, li, td, th, button {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  color: #0F172A;
  -webkit-font-smoothing: antialiased;
}
.main .block-container {
  max-width: 1080px !important;
  padding-top: 0.25rem !important;
  padding-bottom: 3rem !important;
}
/* Aggressively kill Streamlit's default 6rem top padding */
.block-container { padding-top: 0.25rem !important; }
section[data-testid="stMain"] > div { padding-top: 0 !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── App header ── */
.app-header {
  display: flex; align-items: center; gap: 18px;
  padding: 0.75rem 0 0.75rem;
  border-bottom: 2px solid #E2E8F0;
  margin-bottom: 1rem;
}
.app-icon {
  width: 170px; height: 72px;
  background: #FFFFFF;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  border: 1.5px solid #E2E8F0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.10);
}
.app-icon img {
  width: 100%; height: 100%;
  object-fit: contain;
  padding: 8px 10px;
}
.app-header h1 {
  font-size: 28px; font-weight: 800;
  color: #0F172A !important; margin: 0 0 4px; line-height: 1.15;
  letter-spacing: -0.5px;
}
.app-header p { font-size: 14px; color: #64748B !important; margin: 0; font-weight: 400; }

/* ── Streamlit widget inputs ── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
  background-color: #FFFFFF !important;
  color: #0F172A !important;
  border-color: #CBD5E1 !important;
  border-radius: 8px !important;
  font-size: 14px !important;
}
[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"] > div:focus-within { border-color: #3B82F6 !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important; }
[data-baseweb="menu"]         { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 10px !important; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1) !important; }
[data-baseweb="option"]       { background-color: #FFFFFF !important; color: #0F172A !important; font-size: 13px !important; }
[data-baseweb="option"]:hover { background-color: #EFF6FF !important; color: #1E40AF !important; }

/* ── Navigation tabs ── */
[data-baseweb="tab-list"] {
  background-color: #FFFFFF !important;
  border-bottom: 2px solid #E2E8F0 !important;
  gap: 0 !important;
  padding: 0 !important;
}
[data-baseweb="tab"] {
  background-color: transparent !important;
  color: #64748B !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  padding: .875rem 1.25rem !important;
  border-bottom: 3px solid transparent !important;
  margin-bottom: -2px !important;
  letter-spacing: 0.01em !important;
  transition: color .15s ease, border-color .15s ease !important;
}
[data-baseweb="tab"]:hover { color: #1E40AF !important; background: #F8FAFF !important; }
[aria-selected="true"][data-baseweb="tab"] {
  color: #1E40AF !important;
  border-bottom-color: #1E40AF !important;
  font-weight: 700 !important;
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

/* ── Buttons — secondary ── */
.stButton > button {
  background-color: #FFFFFF !important;
  color: #374151 !important;
  border: 1.5px solid #CBD5E1 !important;
  border-radius: 8px !important;
  font-size: 13.5px !important;
  font-weight: 600 !important;
  height: 40px !important;
  transition: all .2s ease !important;
}
.stButton > button:hover {
  border-color: #93C5FD !important;
  background: #F0F9FF !important;
  color: #1E40AF !important;
}

/* ── Buttons — primary (gradient) ── */
.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, #1E40AF 0%, #2563EB 60%, #3B82F6 100%) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
  height: 40px !important;
  box-shadow: 0 2px 8px rgba(30,64,175,0.35) !important;
  transition: all .2s ease !important;
  letter-spacing: 0.02em !important;
}
.stButton > button[kind="primary"] *,
button[data-testid="stBaseButton-primary"] *,
[data-testid="stBaseButton-primary"] * { color: #FFFFFF !important; }
.stButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {
  background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 60%, #2563EB 100%) !important;
  box-shadow: 0 6px 16px rgba(30,64,175,0.45) !important;
  transform: translateY(-1px) !important;
  color: #FFFFFF !important;
}
.stButton > button[kind="primary"]:hover *,
button[data-testid="stBaseButton-primary"]:hover *,
[data-testid="stBaseButton-primary"]:hover * { color: #FFFFFF !important; }

/* ── Cards ── */
.card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
  margin-bottom: 1rem;
}
.card-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: #1E40AF !important;
  margin-bottom: .625rem;
  display: flex;
  align-items: center;
  gap: 6px;
  padding-bottom: .5rem;
  border-bottom: 2px solid #EFF6FF;
}

/* ── Streamlit bordered container — Select Analysis ── */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: #FFFFFF !important;
  border-radius: 12px !important;
  border: 1.5px solid #E2E8F0 !important;
  padding: .875rem 1.25rem !important;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05) !important;
  margin-bottom: .75rem !important;
}
/* ── Email CTA container — inside tab panels only ── */
[data-baseweb="tab-panel"] [data-testid="stVerticalBlockBorderWrapper"] {
  background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%) !important;
  border: 1.5px solid #BFDBFE !important;
  box-shadow: 0 4px 12px rgba(30,64,175,0.12) !important;
  padding: 1.75rem 2rem !important;
  margin-top: 1.5rem !important;
}

/* ── Badges ── */
.badge { display: inline-flex; align-items: center; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px; letter-spacing: 0.01em; }
.badge-critical { background: #FEE2E2; color: #991B1B !important; border: 1px solid #FECACA; }
.badge-high     { background: #FEF3C7; color: #92400E !important; border: 1px solid #FDE68A; }
.badge-warning  { background: #FEF3C7; color: #92400E !important; border: 1px solid #FDE68A; }
.badge-success  { background: #D1FAE5; color: #065F46 !important; border: 1px solid #A7F3D0; }
.badge-danger   { background: #FEE2E2; color: #991B1B !important; border: 1px solid #FECACA; }
.badge-neutral  { background: #F1F5F9; color: #475569 !important; border: 1px solid #CBD5E1; }
.badge-info     { background: #DBEAFE; color: #1E40AF !important; border: 1px solid #BFDBFE; }

/* ── Score display ── */
.score-big { font-size: 56px; font-weight: 800; line-height: 1; letter-spacing: -2px; }
.score-big.danger  { color: #DC2626 !important; }
.score-big.warning { color: #D97706 !important; }
.score-big.success { color: #059669 !important; }

/* ── Mini score cards ── */
.mini-score-card {
  background: #F8FAFC;
  border: 1.5px solid #E2E8F0;
  border-radius: 10px;
  padding: 1rem .875rem;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  transition: box-shadow .2s ease;
}
.mini-score-card .label  { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: #64748B !important; margin-bottom: 6px; }
.mini-score-card .num    { font-size: 28px; font-weight: 800; line-height: 1; letter-spacing: -1px; }
.mini-score-card .denom  { font-size: 11px; color: #94A3B8 !important; }
.mini-score-card .num.danger  { color: #DC2626 !important; }
.mini-score-card .num.warning { color: #D97706 !important; }
.mini-score-card .num.success { color: #059669 !important; }

/* ── Progress bars ── */
.bar-track { height: 7px; background: #E2E8F0; border-radius: 4px; overflow: hidden; margin-top: 8px; }
.bar-fill  { height: 100%; border-radius: 4px; transition: width .6s ease; }
.bar-fill.danger  { background: linear-gradient(90deg, #DC2626, #EF4444); }
.bar-fill.warning { background: linear-gradient(90deg, #D97706, #F59E0B); }
.bar-fill.success { background: linear-gradient(90deg, #059669, #10B981); }

/* ── AI-readiness dimension rows ── */
.dim-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.dim-label { font-size: 12px; font-weight: 500; color: #475569 !important; min-width: 210px; flex-shrink: 0; }
.dim-track { flex: 1; height: 6px; background: #E2E8F0; border-radius: 4px; overflow: hidden; }
.dim-fill  { height: 100%; border-radius: 4px; transition: width .5s ease; }
.dim-score { font-size: 11px; font-weight: 600; color: #64748B !important; min-width: 44px; text-align: right; }

/* ── Live stream items (compact pastel status rows) ── */
.stream-item {
  display: flex; align-items: center; gap: 10px;
  padding: .45rem .875rem;
  border-radius: 8px;
  margin-bottom: 4px;
  border: 1px solid transparent;
}
.stream-item.done    { background: #ECFDF5; border-color: #A7F3D0; }
.stream-item.running { background: #FFFBEB; border-color: #FDE68A; }
.stream-item.idle    { background: #F8FAFC; border-color: #E2E8F0; }
.stream-dot {
  width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; font-size: 11px; font-weight: 700;
}
.stream-dot.done    { background: linear-gradient(135deg,#059669,#10B981); color: #FFFFFF !important; }
.stream-dot.running { background: linear-gradient(135deg,#D97706,#F59E0B); color: #FFFFFF !important; }
.stream-dot.idle    { background: #CBD5E1; color: #64748B !important; }
.stream-content     { flex: 1; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.stream-title    { font-size: 13px; font-weight: 600; color: #0F172A !important; white-space: nowrap; }
.stream-subtitle { font-size: 11.5px; color: #64748B !important; }
.stream-tags     { display: flex; flex-wrap: wrap; gap: 4px; margin-left: 4px; }
.stream-tag { font-size: 10.5px; background: #FEE2E2; border: 1px solid #FECACA; color: #991B1B !important; padding: 1px 7px; border-radius: 20px; font-weight: 500; }

/* ── Violation cards ── */
.violation {
  border: 1px solid #E2E8F0;
  border-left: 4px solid #E2E8F0;
  border-radius: 0 10px 10px 0;
  padding: 1rem 1.125rem;
  margin-bottom: .875rem;
  background: #FFFFFF;
  transition: box-shadow .2s ease;
}
.violation.critical { border-left-color: #DC2626; background: #FFFAFA; }
.violation.high     { border-left-color: #D97706; background: #FFFCF5; }
.violation.medium   { border-left-color: #F59E0B; background: #FFFDF0; }
.violation-header   { display: flex; align-items: center; justify-content: space-between; margin-bottom: .5rem; flex-wrap: wrap; gap: 6px; }
.violation-meta     { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.violation-deduction      { font-size: 12px; font-weight: 700; color: #991B1B !important; background: #FEE2E2; padding: 2px 8px; border-radius: 6px; }
.violation-deduction.high { color: #92400E !important; background: #FEF3C7; }
.violation-desc { font-size: 13.5px; color: #1E293B !important; margin-bottom: .35rem; line-height: 1.55; font-weight: 400; }
.violation-rule { font-size: 11px; color: #94A3B8 !important; margin-bottom: .25rem; font-style: italic; }
.mono {
  font-family: 'Fira Code', 'SF Mono', 'Cascadia Code', monospace;
  font-size: 11.5px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  padding: 4px 10px;
  border-radius: 6px;
  color: #475569 !important;
  display: inline-block;
  max-width: 100%;
  word-break: break-word;
  margin-top: 6px;
}

/* ── Before / After ── */
.before-after { display: grid; grid-template-columns: 1fr 1fr; gap: .875rem; margin-bottom: 1.25rem; }
.before-box { background: #FFF1F2; border: 1.5px solid #FECDD3; border-radius: 10px; padding: 1rem; }
.after-box  { background: #F0FDF4; border: 1.5px solid #BBF7D0; border-radius: 10px; padding: 1rem; }
.ba-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; margin-bottom: 7px; display: flex; justify-content: space-between; }
.before-box .ba-label { color: #BE123C !important; }
.after-box  .ba-label { color: #166534 !important; }
.before-box p { font-size: 13px; color: #9F1239 !important; line-height: 1.6; margin: 0; }
.after-box  p { font-size: 13px; color: #15803D !important; line-height: 1.6; margin: 0; }

/* ── Bullet compare ── */
.bullet-list { border: 1.5px solid #E2E8F0; border-radius: 10px; overflow: hidden; }
.bullet-item { padding: .5rem .875rem; font-size: 12.5px; color: #475569 !important; border-bottom: 1px solid #E2E8F0; background: #FFFFFF; line-height: 1.5; }
.bullet-item:last-child { border-bottom: none; }
.bullet-item.bad  { background: #FFF1F2; color: #BE123C !important; }
.bullet-item.good { background: #F0FDF4; color: #166534 !important; }

/* ── Change notes ── */
.change-note { display: flex; align-items: flex-start; gap: 10px; padding: .625rem 0; border-bottom: 1px solid #F1F5F9; font-size: 12.5px; }
.change-note:last-child { border-bottom: none; }
.change-note .icon { flex-shrink: 0; margin-top: 1px; font-size: 15px; }

/* ── Callout ── */
.callout { background: #EFF6FF; border: 1.5px solid #BFDBFE; border-radius: 10px; padding: 1rem 1.125rem; margin-bottom: .875rem; border-left: 4px solid #3B82F6; }
.callout-title { font-size: 12.5px; font-weight: 700; color: #1E40AF !important; margin-bottom: 4px; }
.callout-body  { font-size: 12.5px; color: #1D4ED8 !important; line-height: 1.55; }

/* ── Session history table ── */
.history-table { width: 100%; border-collapse: collapse; }
.history-table th { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: #64748B !important; text-align: left; padding: .75rem 1rem; background: #F8FAFC; border-bottom: 2px solid #E2E8F0; }
.history-table td { padding: .75rem 1rem; font-size: 13px; color: #1E293B !important; border-bottom: 1px solid #F1F5F9; vertical-align: middle; background: #FFFFFF; }
.history-table tr:last-child td { border-bottom: none; }
.history-table tr:hover td { background: #F8FAFF !important; }

/* ── Empty state ── */
.empty-state { text-align: center; padding: 4rem 1rem; }
.empty-state .icon { font-size: 40px; margin-bottom: 1rem; opacity: .7; }
.empty-state p { font-size: 14px; color: #94A3B8 !important; }

/* ── Misc ── */
.note    { font-size: 11.5px; color: #94A3B8 !important; font-style: italic; margin-top: .625rem; }
.divider { height: 1px; background: #E2E8F0; margin: 1.25rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────

if "results_history" not in st.session_state:
    st.session_state["results_history"] = []
if "current_result" not in st.session_state:
    st.session_state["current_result"] = None
if "analysis_done" not in st.session_state:
    st.session_state["analysis_done"] = False

# ── App header ────────────────────────────────────────────────────────────────

st.markdown(
    f'<div class="app-header">'
    f'<div class="app-icon"><img src="{_LOGO_SRC}" alt="Mars Petcare" /></div>'
    f'<div>'
    f'<h1>AI-Ready Digital Shelf Agent</h1>'
    f'<p>Mars Petcare · Dry Dog Food · Amazon &amp; Walmart</p>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Persistent controls (above tabs — always visible) ────────────────────────

with st.container(border=True):
    st.markdown(
        '<p style="font-size:13px;font-weight:700;text-transform:uppercase;'
        'letter-spacing:.05em;color:#1e3a8a;margin:0 0 .75rem">🎯 Select analysis</p>',
        unsafe_allow_html=True,
    )
    col_sku, col_ret, col_btn = st.columns([2, 1.2, 1])
    with col_sku:
        st.markdown('<p style="font-size:12px;color:#374151;font-weight:500;margin-bottom:4px">SKU</p>', unsafe_allow_html=True)
        sku_choice = st.selectbox(
            "SKU",
            options=["pedigree_compnutr", "iams_minichunks", "iams_largebreed"],
            format_func=lambda x: {
                "pedigree_compnutr": "Pedigree Complete Nutrition Adult 30lb",
                "iams_minichunks":   "IAMS ProActive Health Adult MiniChunks 30lb",
                "iams_largebreed":   "IAMS ProActive Health Large Breed Adult 30lb",
            }[x],
            label_visibility="collapsed",
            key="global_sku",
        )
    with col_ret:
        st.markdown('<p style="font-size:12px;color:#374151;font-weight:500;margin-bottom:4px">Retailer</p>', unsafe_allow_html=True)
        retailer_choice = st.selectbox(
            "Retailer",
            options=["amazon", "walmart"],
            format_func=lambda x: x.capitalize(),
            label_visibility="collapsed",
            key="global_retailer",
        )
    with col_btn:
        st.markdown('<p style="font-size:12px;color:#374151;font-weight:500;margin-bottom:4px">&nbsp;</p>', unsafe_allow_html=True)
        run_analysis = st.button("▶ Analyze shelf", type="primary", use_container_width=True)

# ── Tab labels ────────────────────────────────────────────────────────────────

result = st.session_state.get("current_result")

tab_analyze, tab_recovery, tab_logs = st.tabs([
    "📊  Scorecard",
    "✏️  Recovery",
    "📋  Agent Run Logs",
])

# ══════════════════════════════════════════════════════
# TAB 1 — ANALYZE
# ══════════════════════════════════════════════════════

with tab_analyze:

    # ── helpers defined once at the top of this tab ───────────────────────────
    def _node_items(statuses: dict, tags: list) -> str:
        rows = [
            ("shelf_scanner",      "1", "Shelf scanner",             "Waiting…"),
            ("compliance_agent",   "2", "Compliance + AI-readiness", "Waiting…"),
            ("recovery_generator", "3", "Recovery generator",        "Waiting…"),
        ]
        parts = []
        for node_id, num, title, default_sub in rows:
            state_cls = statuses.get(node_id, "idle")
            sub       = _html.escape(statuses.get(node_id + "_sub", default_sub), quote=False)
            dot       = "✓" if state_cls == "done" else ("…" if state_cls == "running" else num)
            tag_html  = ""
            if node_id == "compliance_agent" and tags and state_cls in ("running", "done"):
                spans = "".join(f'<span class="stream-tag">⚠ {_html.escape(t, quote=False)}</span>' for t in tags)
                tag_html = f'<div class="stream-tags">{spans}</div>'
            # NO indentation — indented lines become Markdown code blocks
            parts.append(
                f'<div class="stream-item {state_cls}">'
                f'<div class="stream-dot {state_cls}">{dot}</div>'
                f'<div class="stream-content">'
                f'<span class="stream-title">{title}</span>'
                f'<span class="stream-subtitle">— {sub}</span>'
                f'{tag_html}'
                f'</div></div>'
            )
        return "".join(parts)

    def _live_card(statuses: dict, tags: list, complete: bool = False) -> str:
        nodes = _node_items(statuses, tags)
        footer = ""
        if complete:
            footer = (
                '<div style="border-top:1px solid #E2E8F0;margin-top:.625rem;padding-top:.5rem;'
                'display:flex;align-items:center;gap:8px">'
                '<span style="font-size:12px;color:#059669;font-weight:600">'
                '✓ Analysis complete</span>'
                '<span style="font-size:11.5px;color:#64748B">— Scorecard and Recovery tabs are now populated</span>'
                '</div>'
            )
        return (
            '<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;'
            'padding:.875rem 1.125rem;box-shadow:0 4px 6px -1px rgba(0,0,0,0.07);margin-bottom:1rem">'
            '<div style="font-size:11px;font-weight:700;text-transform:uppercase;'
            'letter-spacing:.08em;color:#1E40AF;margin-bottom:.5rem;padding-bottom:.375rem;'
            'border-bottom:2px solid #EFF6FF">⚡ Live Agent Run Log</div>'
            f'<div style="display:flex;flex-direction:column;gap:3px">{nodes}</div>'
            f'{footer}'
            '</div>'
        )

    # ── Live output card — ONE placeholder, entirely self-contained HTML ───────
    live_ph = st.empty()

    if not run_analysis and not st.session_state["analysis_done"]:
        live_ph.markdown(
            '<div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;'
            'padding:1.25rem 1.5rem;box-shadow:0 1px 3px rgba(0,0,0,0.06);margin-bottom:1rem">'
            '<div style="font-size:11px;font-weight:600;text-transform:uppercase;'
            'letter-spacing:.05em;color:#1e3a8a;margin-bottom:.875rem">⚡ Live Agent Run Log</div>'
            '<div style="text-align:center;padding:3rem 1rem">'
            '<div style="font-size:36px;margin-bottom:.75rem">📋</div>'
            '<p style="font-size:13px;color:#9ca3af">Select a SKU and retailer above, then click Analyze to begin.</p>'
            '</div></div>',
            unsafe_allow_html=True,
        )

    if run_analysis:
        st.session_state["analysis_done"] = False
        st.session_state["current_result"] = None

        statuses: dict = {}
        violation_tags: list = []

        # Node 1 starting
        statuses["shelf_scanner"] = "running"
        statuses["shelf_scanner_sub"] = "Extracting content from product page…"
        live_ph.markdown(_live_card(statuses, violation_tags), unsafe_allow_html=True)

        full_state: dict = {}
        try:
            for chunk in compiled_graph.stream(
                {"sku_id": sku_choice, "retailer": retailer_choice},
                stream_mode="updates",
            ):
                node_name = list(chunk.keys())[0]
                node_data = chunk[node_name]
                full_state.update(node_data)

                if node_name == "shelf_scanner":
                    pd = node_data.get("product_data", {})
                    statuses["shelf_scanner"] = "done"
                    statuses["shelf_scanner_sub"] = (
                        f"Title ({len(pd.get('title',''))} chars), "
                        f"{len(pd.get('bullets',[]))} bullets, description extracted"
                    )
                    statuses["compliance_agent"] = "running"
                    statuses["compliance_agent_sub"] = (
                        f"Checking against brand guidelines and {retailer_choice.capitalize()} rules…"
                    )
                    live_ph.markdown(_live_card(statuses, violation_tags), unsafe_allow_html=True)

                elif node_name == "compliance_agent":
                    violations = node_data.get("violations", [])
                    scores     = node_data.get("scores", {})
                    violation_tags = [
                        v.get("rule_description", v.get("field", ""))[:40]
                        for v in violations[:3]
                    ]
                    statuses["compliance_agent"] = "done"
                    statuses["compliance_agent_sub"] = (
                        f"{len(violations)} violations found · Score: {scores.get('total_score', 0)} / 100"
                    )
                    statuses["recovery_generator"] = "running"
                    statuses["recovery_generator_sub"] = "Rewriting title, bullets, and description…"
                    live_ph.markdown(_live_card(statuses, violation_tags), unsafe_allow_html=True)

                elif node_name == "recovery_generator":
                    rec = node_data.get("recovered", {})
                    statuses["recovery_generator"] = "done"
                    statuses["recovery_generator_sub"] = (
                        f"Corrective content ready — title, "
                        f"{len(rec.get('recovered_bullets', []))} bullets, description"
                    )
                    live_ph.markdown(_live_card(statuses, violation_tags, complete=True), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

        full_state["sku_id"]    = sku_choice
        full_state["retailer"]  = retailer_choice
        st.session_state["current_result"] = full_state
        st.session_state["analysis_done"]  = True

        scores = full_state.get("scores", {})
        st.session_state["results_history"].append({
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M"),
            "sku_id":      sku_choice,
            "retailer":    retailer_choice,
            "total_score": scores.get("total_score", 0),
            "tier_label":  scores.get("tier_label", ""),
            "tier_emoji":  scores.get("tier_emoji", ""),
            "result":      full_state,
        })
        # Rerun so all tabs re-evaluate with the new result in session_state
        st.rerun()

    elif st.session_state["analysis_done"] and result:
        # Show completed state on page reload / tab switch
        pd_     = result.get("product_data", {})
        rec_    = result.get("recovered", {})
        viols_  = result.get("violations", [])
        sc_     = result.get("scores", {})
        tags_   = [v.get("rule_description", "")[:40] for v in viols_[:3]]
        static_statuses = {
            "shelf_scanner":          "done",
            "shelf_scanner_sub":      f"Title ({len(pd_.get('title',''))} chars), {len(pd_.get('bullets',[]))} bullets, description extracted",
            "compliance_agent":       "done",
            "compliance_agent_sub":   f"{len(viols_)} violations found · Score: {sc_.get('total_score',0)} / 100",
            "recovery_generator":     "done",
            "recovery_generator_sub": f"Corrective content ready — title, {len(rec_.get('recovered_bullets',[]))} bullets, description",
        }
        live_ph.markdown(_live_card(static_statuses, tags_, complete=True), unsafe_allow_html=True)

    # ── Scorecard — shown below live output once analysis is done ─────────────
    result = st.session_state.get("current_result")
    if result:
        scores = result["scores"]
        violations = result.get("violations", [])
        ai_dims = result.get("ai_dimensions", {})
        retailer = result.get("retailer", "")
        sku_id = result.get("sku_id", "")

        total = scores["total_score"]
        tier = scores["tier_label"]
        tier_emoji = scores["tier_emoji"]
        brand_s = scores["brand_score"]
        platform_s = scores["platform_score"]
        ai_s = scores["ai_readiness_score"]
        critical_c = scores["critical_count"]
        high_c = scores["high_count"]
        viol_c = scores["violation_count"]

        def score_class(s, mx):
            pct = s / mx if mx else 0
            return "danger" if pct < 0.5 else ("warning" if pct < 0.8 else "success")

        total_cls    = score_class(total, 100)
        brand_cls    = score_class(brand_s, 40)
        platform_cls = score_class(platform_s, 30)
        ai_cls       = score_class(ai_s, 30)

        sku_label = {
            "pedigree_compnutr": "Pedigree Complete Nutrition",
            "iams_minichunks":   "IAMS MiniChunks",
            "iams_largebreed":   "IAMS Large Breed",
        }.get(sku_id, sku_id)

        tier_badge_cls = {"AI-Ready": "success", "Needs Attention": "warning", "At Risk": "warning", "Critical": "danger"}.get(tier, "neutral")

        # Divider between live output and scorecard
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

        # Overall score banner
        _md(f"""
        <div class="card">
          <div class="card-title">📊 Scorecard</div>
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem">
            <div style="display:flex;align-items:center;gap:1.125rem">
              <div>
                <div class="score-big {total_cls}">{total}</div>
                <div style="font-size:12px;color:#9ca3af;text-align:center">/ 100</div>
              </div>
              <div>
                <span class="badge badge-{tier_badge_cls}" style="font-size:13px;padding:5px 14px;border-radius:6px">
                  {tier_emoji} {tier}
                </span>
                <p style="font-size:12px;color:#6b7280;margin-top:6px;margin-bottom:2px">{sku_label} · {retailer.capitalize()}</p>
                <p style="font-size:12px;color:#6b7280;margin:0">{viol_c} violations &nbsp;·&nbsp; {critical_c} critical &nbsp;·&nbsp; {high_c} high</p>
              </div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.75rem;min-width:300px">
              <div class="mini-score-card">
                <div class="label">Brand compliance</div>
                <div class="num {brand_cls}">{brand_s}</div>
                <div class="denom">/ 40</div>
                <div class="bar-track"><div class="bar-fill {brand_cls}" style="width:{int(brand_s/40*100)}%"></div></div>
              </div>
              <div class="mini-score-card">
                <div class="label">Platform rules</div>
                <div class="num {platform_cls}">{platform_s}</div>
                <div class="denom">/ 30</div>
                <div class="bar-track"><div class="bar-fill {platform_cls}" style="width:{int(platform_s/30*100)}%"></div></div>
              </div>
              <div class="mini-score-card">
                <div class="label">AI-readiness</div>
                <div class="num {ai_cls}">{ai_s}</div>
                <div class="denom">/ 30</div>
                <div class="bar-track"><div class="bar-fill {ai_cls}" style="width:{int(ai_s/30*100)}%"></div></div>
              </div>
            </div>
          </div>
        </div>
        """)

        # Compliance + AI-readiness side by side
        col_comp, col_ai = st.columns(2)

        with col_comp:
            section_a = [v for v in violations if v.get("section") == "A"]
            section_b = [v for v in violations if v.get("section") == "B"]
            a_crit = sum(1 for v in section_a if v.get("severity", "").lower() == "critical")
            a_high = sum(1 for v in section_a if v.get("severity", "").lower() == "high")
            b_crit = sum(1 for v in section_b if v.get("severity", "").lower() == "critical")
            b_high = sum(1 for v in section_b if v.get("severity", "").lower() == "high")
            _md(f"""
            <div class="card">
              <div class="card-title">📋 Compliance breakdown</div>
              <div style="margin-bottom:1rem">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                  <span style="font-size:13px;font-weight:500">Brand guidelines</span>
                  <span style="font-size:13px;font-weight:600;color:{'#dc2626' if brand_s < 30 else '#d97706' if brand_s < 40 else '#16a34a'}">{brand_s} / 40</span>
                </div>
                <div class="bar-track"><div class="bar-fill {brand_cls}" style="width:{int(brand_s/40*100)}%"></div></div>
                <div style="display:flex;gap:5px;margin-top:6px">
                  {'<span class="badge badge-critical">' + str(a_crit) + ' critical</span>' if a_crit else ''}
                  {'<span class="badge badge-high">' + str(a_high) + ' high</span>' if a_high else ''}
                  {'<span class="badge badge-success">No violations</span>' if not section_a else ''}
                </div>
              </div>
              <div class="divider"></div>
              <div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                  <span style="font-size:13px;font-weight:500">{retailer.capitalize()} platform rules</span>
                  <span style="font-size:13px;font-weight:600;color:{'#dc2626' if platform_s < 20 else '#d97706' if platform_s < 30 else '#16a34a'}">{platform_s} / 30</span>
                </div>
                <div class="bar-track"><div class="bar-fill {platform_cls}" style="width:{int(platform_s/30*100)}%"></div></div>
                <div style="display:flex;gap:5px;margin-top:6px">
                  {'<span class="badge badge-critical">' + str(b_crit) + ' critical</span>' if b_crit else ''}
                  {'<span class="badge badge-high">' + str(b_high) + ' high</span>' if b_high else ''}
                  {'<span class="badge badge-success">No violations</span>' if not section_b else ''}
                </div>
              </div>
            </div>
            """)

        with col_ai:
            ai_assistant = "Rufus (Amazon)" if retailer == "amazon" else "Sparky (Walmart)"
            dims_html = ""
            for dim_id, dim in ai_dims.items():
                pct = int((dim["score"] / dim["max_score"] * 100)) if dim["max_score"] else 0
                color = "#dc2626" if pct < 40 else ("#d97706" if pct < 70 else "#16a34a")
                dims_html += (
                    f'<div class="dim-row">'
                    f'<span class="dim-label">{dim["label"]}</span>'
                    f'<div class="dim-track"><div class="dim-fill" style="width:{pct}%;background:{color}"></div></div>'
                    f'<span class="dim-score">{dim["score"]} / {dim["max_score"]}</span>'
                    f'</div>'
                )
            ai_score_color = '#dc2626' if ai_s < 12 else ('#d97706' if ai_s < 22 else '#16a34a')
            _md(
                f'<div class="card">'
                f'<div class="card-title">🤖 AI-readiness — {ai_assistant}</div>'
                f'{dims_html}'
                f'<div class="divider"></div>'
                f'<div style="display:flex;justify-content:space-between">'
                f'<span style="font-size:12px;color:#6b7280">Total AI-readiness score</span>'
                f'<span style="font-size:14px;font-weight:600;color:{ai_score_color}">{ai_s} / 30</span>'
                f'</div></div>'
            )

        # Violations
        if violations:
            cross_retailer_risk = None
            for v in violations:
                if "domestically" in v.get("rule_description", "").lower() or \
                   "made in usa" in v.get("rule_description", "").lower():
                    cross_retailer_risk = v.get("rule_description", "")
                    break

            viol_inner = ""
            if cross_retailer_risk:
                viol_inner += (
                    f'<div class="callout">'
                    f'<div class="callout-title">🔁 Cross-retailer risk detected</div>'
                    f'<div class="callout-body">{_html.escape(cross_retailer_risk, quote=False)}'
                    f' — content copied across retailers without platform-specific checks will miss this.</div>'
                    f'</div>'
                )
            for v in violations:
                sev           = v.get("severity", "medium").lower()
                section       = v.get("section", "")
                section_label = "Brand guidelines" if section == "A" else "Platform rules"
                section_badge = "neutral" if section == "A" else "info"
                field         = v.get("field", "")
                desc          = _html.escape(v.get("rule_description", v.get("description", "")), quote=False)
                quoted        = _html.escape(v.get("quoted_text", ""), quote=False)
                rule_id       = v.get("rule_id", "")
                deduction     = v.get("points_deduction", "")
                deduction_sign = f"−{deduction} pts" if deduction else ""
                deduction_cls  = "high" if sev == "high" else ""
                quoted_html   = f'<div class="mono" style="margin-top:5px">{quoted}</div>' if quoted else ""
                viol_inner += (
                    f'<div class="violation {sev}">'
                    f'<div class="violation-header">'
                    f'<div class="violation-meta">'
                    f'<span class="badge badge-{sev}">{sev.capitalize()}</span>'
                    f'<span class="badge badge-{section_badge}">{section_label}</span>'
                    f'<span style="font-size:11px;color:#9ca3af">{field.capitalize()}</span>'
                    f'</div>'
                    f'<span class="violation-deduction {deduction_cls}">{deduction_sign}</span>'
                    f'</div>'
                    f'<p class="violation-desc">{desc}</p>'
                    f'{quoted_html}'
                    f'<div class="violation-rule">Rule: {rule_id}</div>'
                    f'</div>'
                )
            _md(
                f'<div class="card">'
                f'<div class="card-title">⚠ Violations ({len(violations)} found)</div>'
                f'{viol_inner}'
                f'</div>'
            )


# ══════════════════════════════════════════════════════
# TAB 3 — RECOVERY
# ══════════════════════════════════════════════════════

with tab_recovery:
    result = st.session_state.get("current_result")
    if not result:
        _md("""
        <div class="empty-state">
          <div class="icon">✏️</div>
          <p>Run an analysis first to see recovery content.</p>
        </div>
        """)
    else:
        recovered    = result.get("recovered", {})
        product_data = result.get("product_data", {})

        orig_title   = _html.escape(product_data.get("title", ""), quote=False)
        new_title    = _html.escape(recovered.get("recovered_title", ""), quote=False)
        orig_bullets = product_data.get("bullets", [])
        new_bullets  = recovered.get("recovered_bullets", [])
        new_desc     = _html.escape(recovered.get("recovered_description", ""), quote=False)
        change_notes = recovered.get("change_notes", [])

        orig_chars = len(product_data.get("title", ""))
        new_chars  = len(recovered.get("recovered_title", ""))
        orig_char_label = f"{orig_chars} chars" + (" — over 90-char ideal" if orig_chars > 90 else "")
        new_char_label  = f"{new_chars} chars ✓" if new_chars <= 90 else f"{new_chars} chars"

        # Title before/after
        _md(f"""
        <div class="card">
          <div class="card-title" style="margin-bottom:.75rem">✏️ Title</div>
          <div class="before-after">
            <div class="before-box">
              <div class="ba-label"><span>Before</span><span>{orig_char_label}</span></div>
              <p>{orig_title}</p>
            </div>
            <div class="after-box">
              <div class="ba-label"><span>After</span><span>{new_char_label}</span></div>
              <p>{new_title}</p>
            </div>
          </div>
        </div>
        """)

        # Bullets before/after
        orig_bullet_html = "".join(
            f'<div class="bullet-item bad">{_html.escape(b, quote=False)}</div>' for b in orig_bullets
        )
        new_bullet_html = "".join(
            f'<div class="bullet-item good">{_html.escape(b, quote=False)}</div>' for b in new_bullets
        )
        _md(f"""
        <div class="card">
          <div class="card-title" style="margin-bottom:.75rem">📝 Bullet points</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:.75rem;margin-bottom:.5rem">
            <div>
              <p style="font-size:10px;font-weight:600;color:#b91c1c;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px">Before — {len(orig_bullets)} bullets</p>
              <div class="bullet-list">{orig_bullet_html}</div>
            </div>
            <div>
              <p style="font-size:10px;font-weight:600;color:#15803d;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px">After — {len(new_bullets)} bullets (compliant)</p>
              <div class="bullet-list">{new_bullet_html}</div>
            </div>
          </div>
        </div>
        """)

        # Description
        _md(f"""
        <div class="card">
          <div class="card-title" style="margin-bottom:.75rem">📄 Description</div>
          <div class="after-box">
            <div class="ba-label"><span>Recovered description (compliant with both Amazon &amp; Walmart)</span></div>
            <p style="line-height:1.65">{new_desc}</p>
          </div>
        </div>
        """)

        # Change notes
        if change_notes:
            notes_inner = ""
            for note in change_notes:
                ntype  = note.get("type", "")
                desc   = _html.escape(note.get("description", ""), quote=False)
                rule   = note.get("fix_for_rule", "")
                icon   = "✕" if ntype == "removed" else ("+" if ntype == "added" else "↔")
                colour = "#b91c1c" if ntype == "removed" else ("#16a34a" if ntype == "added" else "#d97706")
                rule_span = f' <span style="font-size:10px;color:#9ca3af">({rule})</span>' if rule else ""
                notes_inner += (
                    f'<div class="change-note">'
                    f'<span class="icon" style="color:{colour}">{icon}</span>'
                    f'<div style="color:{colour}">{desc}{rule_span}</div>'
                    f'</div>'
                )
            _md(
                f'<div class="card">'
                f'<div class="card-title" style="margin-bottom:.75rem">🔖 Change notes</div>'
                f'{notes_inner}'
                f'</div>'
            )

        # ── Email report — entire section inside one bordered container ────────
        rec_result = st.session_state.get("current_result")
        with st.container(border=True):
            # Header (markdown safe — no widgets here)
            st.markdown(
                '<div style="display:flex;align-items:center;gap:14px;margin-bottom:1rem">'
                '<div style="width:48px;height:48px;background:#2563eb;border-radius:10px;'
                'display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0">📨</div>'
                '<div>'
                '<div style="font-size:18px;font-weight:700;color:#1e3a8a;margin-bottom:3px">Email this report</div>'
                '<div style="font-size:13px;color:#1d4ed8">Send the full gap analysis — score, violations &amp; recovered content — as a formatted HTML email</div>'
                '</div></div>'
                '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:1.25rem">'
                '<span style="background:#dbeafe;color:#1e40af;font-size:11px;font-weight:500;padding:3px 10px;border-radius:20px;border:1px solid #93c5fd">✓ Overall score &amp; tier</span>'
                '<span style="background:#dbeafe;color:#1e40af;font-size:11px;font-weight:500;padding:3px 10px;border-radius:20px;border:1px solid #93c5fd">✓ All violations with detail</span>'
                '<span style="background:#dbeafe;color:#1e40af;font-size:11px;font-weight:500;padding:3px 10px;border-radius:20px;border:1px solid #93c5fd">✓ Recovered title, bullets &amp; description</span>'
                '<span style="background:#dbeafe;color:#1e40af;font-size:11px;font-weight:500;padding:3px 10px;border-radius:20px;border:1px solid #93c5fd">✓ Change notes</span>'
                '</div>',
                unsafe_allow_html=True,
            )
            if not rec_result:
                st.markdown(
                    '<p style="font-size:13px;color:#1d4ed8;font-style:italic;text-align:center;padding:.5rem 0">'
                    '⚠ Run an analysis first to enable report sending.</p>',
                    unsafe_allow_html=True,
                )
            else:
                rec_col1, rec_col2 = st.columns([4, 1])
                with rec_col1:
                    rec_email = st.text_input(
                        "Recipient email address",
                        placeholder="brand.manager@marspetcare.com",
                        label_visibility="collapsed",
                        key="recovery_email",
                    )
                with rec_col2:
                    rec_send = st.button("📨 Send report", type="primary", use_container_width=True, key="recovery_send_btn")
                if rec_send:
                    if not rec_email:
                        st.warning("Please enter a recipient email address.")
                    else:
                        with st.spinner("Sending report…"):
                            try:
                                send_report(rec_email, rec_result)
                                st.success("✓ Report sent successfully to " + rec_email)
                            except Exception as e:
                                st.error(f"Failed to send: {e}")


# ══════════════════════════════════════════════════════
# TAB 4 — AGENT RUN LOGS
# ══════════════════════════════════════════════════════

_SKU_DISPLAY = {
    "pedigree_compnutr": "Pedigree Complete Nutrition Adult 30lb",
    "iams_minichunks":   "IAMS ProActive Health Adult MiniChunks 30lb",
    "iams_largebreed":   "IAMS ProActive Health Large Breed Adult 30lb",
}

with tab_logs:
    history = st.session_state["results_history"]

    if not history:
        _md("""
        <div class="empty-state">
          <div class="icon">📋</div>
          <p>No analyses run yet this session. Run an analysis to see logs here.</p>
        </div>
        """)
    else:
        rows_html = ""
        for h in history:
            tier        = h["tier_label"]
            badge_cls   = {"AI-Ready": "success", "Needs Attention": "warning", "At Risk": "warning", "Critical": "danger"}.get(tier, "neutral")
            score_col   = "#dc2626" if h["total_score"] < 40 else ("#d97706" if h["total_score"] < 80 else "#16a34a")
            sku_full    = _SKU_DISPLAY.get(h["sku_id"], h["sku_id"])
            rows_html += (
                f'<tr>'
                f'<td style="color:#6b7280">{h["timestamp"]}</td>'
                f'<td style="font-weight:500">{sku_full}</td>'
                f'<td>{h["retailer"].capitalize()}</td>'
                f'<td><span style="font-weight:700;font-size:14px;color:{score_col}">{h["total_score"]}</span>'
                f'<span style="font-size:11px;color:#9ca3af"> / 100</span></td>'
                f'<td><span class="badge badge-{badge_cls}">{h["tier_emoji"]} {tier}</span></td>'
                f'</tr>'
            )

        _md(
            '<div class="card">'
            '<div class="card-title">📋 Agent run logs — current session</div>'
            '<div style="border:1px solid #e5e7eb;border-radius:8px;overflow:hidden">'
            '<table class="history-table">'
            '<thead><tr>'
            '<th>Time</th><th>SKU</th><th>Retailer</th><th>Score</th><th>Tier</th>'
            '</tr></thead>'
            f'<tbody>{rows_html}</tbody>'
            '</table></div>'
            '<p style="font-size:11px;color:#9ca3af;font-style:italic;margin-top:.75rem">'
            'Logs are session-only and reset on page refresh.</p>'
            '</div>'
        )
