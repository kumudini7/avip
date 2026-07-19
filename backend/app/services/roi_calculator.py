from __future__ import annotations

from app.core.config import settings

CHART_MONTHS = 36

# Percentage of current effort/cost still required after automation, by classification category.
AUTOMATION_REMAINING_PCT = {
    "pure_rpa": 15,
    "rpa_ai": 12,
    "rpa_ui": 20,
}

# One-time implementation cost in INR lakhs, by complexity.
IMPLEMENTATION_COST_INR_LAKHS = {
    "low": 5,
    "medium": 15,
    "high": 35,
}


def to_currency(amount_inr: float, currency: str) -> float:
    if currency == "USD":
        return amount_inr / settings.usd_inr_rate
    return amount_inr


def compute_roi(
    *,
    category: str,
    complexity: str,
    volume_per_month: int,
    team_size: int,
    avg_fte_cost: float,
    currency: str,
) -> dict:
    """avg_fte_cost is expected in the same currency the caller wants results in."""

    remaining_pct = AUTOMATION_REMAINING_PCT.get(category, 15)
    implementation_cost_inr = IMPLEMENTATION_COST_INR_LAKHS.get(complexity, 15) * 100_000
    implementation_cost = to_currency(implementation_cost_inr, currency)

    current_annual_cost = team_size * avg_fte_cost
    post_automation_cost = current_annual_cost * remaining_pct / 100
    annual_saving = current_annual_cost - post_automation_cost
    monthly_saving = annual_saving / 12

    year1_net_saving = annual_saving - implementation_cost
    year2_saving = annual_saving

    payback_months: float | None
    if monthly_saving > 0:
        payback_months = round(implementation_cost / monthly_saving, 1)
    else:
        payback_months = None

    chart_series: list[float] = []
    cumulative = -implementation_cost
    for _ in range(CHART_MONTHS):
        cumulative += monthly_saving
        chart_series.append(round(cumulative, 2))

    return {
        "currency": currency,
        "current_annual_cost": round(current_annual_cost, 2),
        "post_automation_cost": round(post_automation_cost, 2),
        "implementation_cost": round(implementation_cost, 2),
        "year1_net_saving": round(year1_net_saving, 2),
        "year2_saving": round(year2_saving, 2),
        "payback_months": payback_months,
        "chart_series": chart_series,
    }
