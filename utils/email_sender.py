import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv

# Load .env from project root regardless of working directory
load_dotenv(Path(__file__).parent.parent / ".env", override=True)


def _severity_colour(sev: str) -> str:
    return {"critical": "#b91c1c", "high": "#b45309", "medium": "#d97706"}.get(sev.lower(), "#6b7280")


def _tier_colour(tier: str) -> str:
    return {
        "AI-Ready": "#16a34a",
        "Needs Attention": "#d97706",
        "At Risk": "#ea580c",
        "Critical": "#dc2626",
    }.get(tier, "#6b7280")


def build_html_report(result: Dict[str, Any]) -> str:
    sku = result.get("sku_id", "")
    retailer = result.get("retailer", "").capitalize()
    scores = result.get("scores", {})
    violations = result.get("violations", [])
    ai_dims = result.get("ai_dimensions", {})
    recovered = result.get("recovered", {})

    total = scores.get("total_score", 0)
    tier = scores.get("tier_label", "")
    tier_colour = _tier_colour(tier)

    viol_rows = ""
    for v in violations:
        sev = v.get("severity", "")
        colour = _severity_colour(sev)
        quoted = v.get("quoted_text", "")
        quoted_html = f'<div style="font-family:monospace;font-size:11px;background:#f8f9fa;border:1px solid #e5e7eb;padding:4px 8px;border-radius:4px;margin-top:4px;color:#6b7280">{quoted}</div>' if quoted else ""
        viol_rows += f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;vertical-align:top">
            <span style="display:inline-block;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;background:{colour}22;color:{colour}">{sev.upper()}</span>
          </td>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;font-size:13px;color:#111827">
            {v.get('rule_description', v.get('description', ''))}
            {quoted_html}
            <div style="font-size:11px;color:#9ca3af;margin-top:3px">Rule: {v.get('rule_id', '')} &nbsp;·&nbsp; Field: {v.get('field', '')}</div>
          </td>
          <td style="padding:8px;border-bottom:1px solid #e5e7eb;font-size:12px;font-weight:600;color:{colour};white-space:nowrap">
            {v.get('points_deduction', '')} pts
          </td>
        </tr>"""

    dim_rows = ""
    for dim_id, dim in ai_dims.items():
        pct = int((dim.get("score", 0) / dim.get("max_score", 1)) * 100)
        dim_rows += f"""
        <tr>
          <td style="padding:6px 8px;font-size:12px;color:#374151">{dim.get('label', dim_id)}</td>
          <td style="padding:6px 8px">
            <div style="background:#f3f4f6;border-radius:3px;height:6px;overflow:hidden">
              <div style="width:{pct}%;height:100%;background:#2563eb;border-radius:3px"></div>
            </div>
          </td>
          <td style="padding:6px 8px;font-size:12px;color:#6b7280;text-align:right">{dim.get('score', 0)} / {dim.get('max_score', 0)}</td>
        </tr>"""

    change_notes_html = ""
    for note in recovered.get("change_notes", []):
        ntype = note.get("type", "")
        icon = "✕" if ntype == "removed" else "+"
        colour = "#b91c1c" if ntype == "removed" else "#16a34a"
        change_notes_html += f'<div style="display:flex;gap:8px;padding:5px 0;border-bottom:1px solid #e5e7eb;font-size:12px"><span style="color:{colour};font-weight:700;flex-shrink:0">{icon}</span><span style="color:{colour}">{note.get("description", "")}</span></div>'

    bullets_before = "".join(f'<li style="color:#b91c1c;font-size:12px;margin-bottom:3px">{b}</li>' for b in result.get("product_data", {}).get("bullets", []))
    bullets_after = "".join(f'<li style="color:#15803d;font-size:12px;margin-bottom:3px">{b}</li>' for b in recovered.get("recovered_bullets", []))

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"/>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;margin:0;padding:20px}}</style>
</head><body>
<div style="max-width:700px;margin:0 auto">

  <div style="background:#1e3a5f;padding:24px 28px;border-radius:12px 12px 0 0">
    <h1 style="color:#fff;font-size:20px;margin:0 0 4px">🛡️ AI-Ready Digital Shelf Agent</h1>
    <p style="color:#93c5fd;font-size:13px;margin:0">Mars Petcare · Gap Report &amp; Recovery Content</p>
  </div>

  <div style="background:#fff;border:1px solid #e5e7eb;padding:24px 28px;margin-top:0">
    <p style="font-size:13px;color:#6b7280;margin:0 0 16px">SKU: <strong>{sku}</strong> &nbsp;·&nbsp; Retailer: <strong>{retailer}</strong></p>

    <div style="display:flex;align-items:center;gap:20px;margin-bottom:20px">
      <div style="text-align:center">
        <div style="font-size:52px;font-weight:700;color:{tier_colour};line-height:1">{total}</div>
        <div style="font-size:12px;color:#9ca3af">/ 100</div>
      </div>
      <div>
        <span style="display:inline-block;padding:5px 14px;border-radius:6px;font-size:13px;font-weight:600;background:{tier_colour}22;color:{tier_colour}">{scores.get('tier_emoji','')} {tier}</span>
        <div style="font-size:12px;color:#6b7280;margin-top:6px">{scores.get('violation_count',0)} violations · {scores.get('critical_count',0)} critical · {scores.get('high_count',0)} high</div>
      </div>
    </div>

    <table style="width:100%;border-collapse:collapse;margin-bottom:20px">
      <tr>
        <td style="padding:8px;text-align:center;background:#f8f9fa;border:1px solid #e5e7eb;border-radius:6px">
          <div style="font-size:11px;color:#9ca3af">Brand Compliance</div>
          <div style="font-size:24px;font-weight:700;color:{_tier_colour('Critical') if scores.get('brand_score',40)<40 else '#16a34a'}">{scores.get('brand_score',0)}</div>
          <div style="font-size:11px;color:#9ca3af">/ 40</div>
        </td>
        <td style="width:10px"></td>
        <td style="padding:8px;text-align:center;background:#f8f9fa;border:1px solid #e5e7eb;border-radius:6px">
          <div style="font-size:11px;color:#9ca3af">Platform Rules</div>
          <div style="font-size:24px;font-weight:700;color:{_tier_colour('Critical') if scores.get('platform_score',30)<30 else '#16a34a'}">{scores.get('platform_score',0)}</div>
          <div style="font-size:11px;color:#9ca3af">/ 30</div>
        </td>
        <td style="width:10px"></td>
        <td style="padding:8px;text-align:center;background:#f8f9fa;border:1px solid #e5e7eb;border-radius:6px">
          <div style="font-size:11px;color:#9ca3af">AI-Readiness</div>
          <div style="font-size:24px;font-weight:700;color:#d97706">{scores.get('ai_readiness_score',0)}</div>
          <div style="font-size:11px;color:#9ca3af">/ 30</div>
        </td>
      </tr>
    </table>

    <h2 style="font-size:14px;font-weight:600;color:#374151;margin:20px 0 10px">⚠ Violations</h2>
    <table style="width:100%;border-collapse:collapse;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden">
      <thead><tr style="background:#f8f9fa">
        <th style="padding:8px;font-size:11px;color:#9ca3af;text-align:left;font-weight:600">SEVERITY</th>
        <th style="padding:8px;font-size:11px;color:#9ca3af;text-align:left;font-weight:600">DESCRIPTION</th>
        <th style="padding:8px;font-size:11px;color:#9ca3af;text-align:left;font-weight:600">IMPACT</th>
      </tr></thead>
      <tbody>{viol_rows}</tbody>
    </table>

    <h2 style="font-size:14px;font-weight:600;color:#374151;margin:24px 0 10px">🤖 AI-Readiness Dimensions</h2>
    <table style="width:100%;border-collapse:collapse;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden">
      <tbody>{dim_rows}</tbody>
    </table>

    <h2 style="font-size:14px;font-weight:600;color:#374151;margin:24px 0 10px">✏️ Recovered Title</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px">
      <div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:12px">
        <div style="font-size:10px;font-weight:700;color:#b91c1c;text-transform:uppercase;margin-bottom:5px">BEFORE</div>
        <p style="font-size:12px;color:#b91c1c;margin:0;line-height:1.5">{result.get('product_data', {}).get('title', '')}</p>
      </div>
      <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:8px;padding:12px">
        <div style="font-size:10px;font-weight:700;color:#15803d;text-transform:uppercase;margin-bottom:5px">AFTER</div>
        <p style="font-size:12px;color:#15803d;margin:0;line-height:1.5">{recovered.get('recovered_title', '')}</p>
      </div>
    </div>

    <h2 style="font-size:14px;font-weight:600;color:#374151;margin:20px 0 10px">📝 Recovered Bullets</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px">
      <div>
        <div style="font-size:10px;font-weight:700;color:#b91c1c;text-transform:uppercase;margin-bottom:5px">BEFORE</div>
        <ul style="margin:0;padding-left:16px">{bullets_before}</ul>
      </div>
      <div>
        <div style="font-size:10px;font-weight:700;color:#15803d;text-transform:uppercase;margin-bottom:5px">AFTER</div>
        <ul style="margin:0;padding-left:16px">{bullets_after}</ul>
      </div>
    </div>

    <h2 style="font-size:14px;font-weight:600;color:#374151;margin:20px 0 10px">📄 Recovered Description</h2>
    <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:8px;padding:12px;margin-bottom:16px">
      <p style="font-size:12px;color:#15803d;margin:0;line-height:1.65">{recovered.get('recovered_description', '')}</p>
    </div>

    <h2 style="font-size:14px;font-weight:600;color:#374151;margin:20px 0 10px">🔖 Change Notes</h2>
    {change_notes_html}
  </div>

  <div style="background:#f8f9fa;border:1px solid #e5e7eb;border-top:none;padding:16px 28px;border-radius:0 0 12px 12px;text-align:center">
    <p style="font-size:11px;color:#9ca3af;margin:0">Generated by AI-Ready Digital Shelf Agent · Mars Petcare</p>
  </div>

</div>
</body></html>"""


def send_report(to_email: str, result: Dict[str, Any]) -> None:
    host     = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port     = int(os.getenv("SMTP_PORT", "587"))
    user     = os.getenv("SMTP_USER", "").strip()
    # Google app passwords are shown with spaces (xxxx xxxx xxxx xxxx) — strip them
    password = os.getenv("SMTP_PASSWORD", "").replace(" ", "").strip()

    if not user or not password:
        raise ValueError("SMTP_USER and SMTP_PASSWORD must be set in .env")

    sku     = result.get("sku_id", "")
    retailer = result.get("retailer", "").capitalize()
    total   = result.get("scores", {}).get("total_score", 0)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Digital Shelf Gap Report: {sku} · {retailer} · Score {total}/100"
    msg["From"]    = user
    msg["To"]      = to_email

    html_body = build_html_report(result)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(host, port, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, password)
        server.sendmail(user, [to_email], msg.as_string())
