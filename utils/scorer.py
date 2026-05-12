from typing import List, Dict, Any

_BRAND_DEDUCTIONS = {"critical": 20, "high": 10, "medium": 5}
_PLATFORM_DEDUCTIONS = {"critical": 15, "high": 8, "medium": 4}

_TIERS = [
    (80, 100, "AI-Ready", "✅"),
    (60, 79, "Needs Attention", "🟡"),
    (40, 59, "At Risk", "🟠"),
    (0, 39, "Critical", "🔴"),
]


def calculate_scores(
    violations: List[Dict[str, Any]],
    ai_dimensions: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    brand_score = 40
    platform_score = 30

    for v in violations:
        section = v.get("section", "")
        severity = v.get("severity", "").lower()
        if section == "A":
            brand_score -= _BRAND_DEDUCTIONS.get(severity, 0)
        elif section == "B":
            platform_score -= _PLATFORM_DEDUCTIONS.get(severity, 0)

    brand_score = max(0, brand_score)
    platform_score = max(0, platform_score)

    # Additive: raw dimension scores sum to ≤100, then × 0.30
    raw_total = sum(d.get("score", 0) for d in ai_dimensions.values())
    raw_max = sum(d.get("max_score", 0) for d in ai_dimensions.values())
    ai_score = int(round((raw_total / raw_max) * 30)) if raw_max > 0 else 0
    ai_score = max(0, min(30, ai_score))

    total = brand_score + platform_score + ai_score

    tier_label, tier_emoji = "Critical", "🔴"
    for lo, hi, label, emoji in _TIERS:
        if lo <= total <= hi:
            tier_label, tier_emoji = label, emoji
            break

    critical_count = sum(1 for v in violations if v.get("severity", "").lower() == "critical")
    high_count = sum(1 for v in violations if v.get("severity", "").lower() == "high")

    return {
        "brand_score": brand_score,
        "platform_score": platform_score,
        "ai_readiness_score": ai_score,
        "ai_raw_score": raw_total,
        "total_score": total,
        "tier_label": tier_label,
        "tier_emoji": tier_emoji,
        "critical_count": critical_count,
        "high_count": high_count,
        "violation_count": len(violations),
    }
