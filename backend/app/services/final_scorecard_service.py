"""Deterministic scoring for the 8-block executive dashboard: Business
Objective, Process DNA, Decision Complexity, AI Readiness, Automation
Opportunity Heatmap, Value Proposition, Business Case, and the final weighted
Scorecard. Runs entirely off the same questionnaire answers dict as
readiness_scoring_service.compute_scores plus the already-computed
classification/ROI - nothing here is hardcoded per assessment.
"""

from __future__ import annotations

from app.data.questionnaire import BUSINESS_OBJECTIVE_OPTIONS
from app.services.roi_calculator import AUTOMATION_REMAINING_PCT

_DEFAULT_RATING = 3
_DEFAULT_PERCENT = 50

_OBJECTIVE_OUTCOMES = {
    "reduce_cost": "Cost Saving",
    "improve_cx": "Customer Experience Improvement",
    "increase_revenue": "Revenue Growth",
    "improve_compliance": "Compliance Assurance",
    "reduce_risk": "Risk Reduction",
    "improve_quality": "Quality Improvement",
}


def _rating(answers: dict, key: str) -> int:
    value = answers.get(key, _DEFAULT_RATING)
    try:
        value = int(value)
    except (TypeError, ValueError):
        return _DEFAULT_RATING
    return min(5, max(1, value))


def _percent(answers: dict, key: str) -> int:
    value = answers.get(key, _DEFAULT_PERCENT)
    try:
        value = float(value)
    except (TypeError, ValueError):
        return _DEFAULT_PERCENT
    return min(100, max(0, round(value)))


def _multi(answers: dict, key: str) -> list[str]:
    value = answers.get(key, [])
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _to_100(rating_avg: float) -> int:
    return round((rating_avg - 1) / 4 * 100)


def _business_objectives(answers: dict) -> dict:
    selected = set(_multi(answers, "business_objectives"))
    options = [
        {"key": option["key"], "label": option["label"], "selected": option["key"] in selected}
        for option in BUSINESS_OBJECTIVE_OPTIONS
    ]
    return {"options": options, "selected_keys": [o["key"] for o in options if o["selected"]]}


def _process_dna(answers: dict) -> dict:
    raw = {
        "Rule Based": _percent(answers, "process_dna_rule_based"),
        "Human Judgment": _percent(answers, "process_dna_human_judgment"),
        "Knowledge Dependency": _percent(answers, "process_dna_knowledge_dependency"),
        "Creativity": _percent(answers, "process_dna_creativity"),
        "Collaboration": _percent(answers, "process_dna_collaboration"),
    }

    dominant_name, _ = max(
        (
            ("Rule Based", raw["Rule Based"]),
            ("Human Judgment", raw["Human Judgment"]),
            ("Knowledge Dependency", raw["Knowledge Dependency"]),
        ),
        key=lambda pair: pair[1],
    )
    fit_map = {"Rule Based": "RPA", "Human Judgment": "AI", "Knowledge Dependency": "Agentic AI"}
    fit = fit_map[dominant_name]

    return {
        "characteristics": [{"name": name, "pct": pct} for name, pct in raw.items()],
        "dominant_characteristic": dominant_name,
        "interpretation": f"High {dominant_name} -> {fit}",
        "fit": fit,
        "raw": raw,
    }


def _decision_complexity(answers: dict) -> dict:
    parameters = {
        "Structured Data": _rating(answers, "data_type"),
        "Exception Rate": _rating(answers, "exception_rate"),
        "Number of Systems": _rating(answers, "system_integration_complexity"),
        "Reasoning Required": _rating(answers, "human_judgment_frequency"),
        "Recommendations Needed": _rating(answers, "recommendations_needed"),
        "Risk of Wrong Decision": _rating(answers, "risk_of_wrong_decision"),
    }
    scored = {name: _to_100(value) for name, value in parameters.items()}
    complexity_score = round(sum(scored.values()) / len(scored))
    return {
        "parameters": [{"name": name, "score": score} for name, score in scored.items()],
        "complexity_score": complexity_score,
    }


def _ai_readiness(answers: dict) -> dict:
    areas = {
        "Data": _rating(answers, "ai_data_readiness"),
        "Infrastructure": _rating(answers, "ai_infrastructure_readiness"),
        "Governance": _rating(answers, "ai_governance_maturity"),
        "AI Skills": _rating(answers, "ai_skills_readiness"),
        "Existing Automation": _rating(answers, "automation_landscape"),
    }
    scored = {name: _to_100(value) for name, value in areas.items()}
    ai_readiness_pct = round(sum(scored.values()) / len(scored))
    return {
        "areas": [{"name": name, "score": score} for name, score in scored.items()],
        "ai_readiness_pct": ai_readiness_pct,
    }


def _automation_heatmap(process_dna: dict, decision_complexity: dict) -> dict:
    fit = process_dna["fit"]
    complexity_score = decision_complexity["complexity_score"]
    lanes = {"manual": False, "rpa": False, "ai": False, "agentic": False}

    if fit == "RPA":
        lanes["rpa"] = True
        if complexity_score >= 60:
            lanes["ai"] = True
    elif fit == "AI":
        lanes["ai"] = True
        if process_dna["raw"]["Rule Based"] >= 40:
            lanes["rpa"] = True
    else:  # Agentic AI
        lanes["agentic"] = True
        lanes["ai"] = True

    if max(process_dna["raw"].values()) < 30 and complexity_score < 30:
        lanes = {"manual": True, "rpa": False, "ai": False, "agentic": False}

    return {"rows": [{"process_step": "This process", "lanes": lanes}]}


def _value_proposition(business_objectives: dict, matched_use_case: str | None) -> list[dict]:
    opportunity = matched_use_case or "This automation opportunity"
    return [
        {"opportunity": opportunity, "business_outcome": _OBJECTIVE_OUTCOMES[key]}
        for key in business_objectives["selected_keys"]
    ]


def _business_case(
    answers: dict,
    category: str,
    automation_maturity_score: float,
    roi: dict | None,
) -> dict:
    remaining_pct = AUTOMATION_REMAINING_PCT.get(category, 15)
    coverage = 1 - remaining_pct / 100  # fraction of the improvement gap automation closes

    compliance_before = _percent(answers, "current_compliance_rate")
    compliance_after = min(100, round(compliance_before + (100 - compliance_before) * coverage))

    error_before = _percent(answers, "current_error_rate")
    error_after = round(error_before * (remaining_pct / 100))

    cycle_time_before = max(0, round(100 - automation_maturity_score))
    cycle_time_after = round(cycle_time_before * (remaining_pct / 100))

    quality_before = _to_100(6 - _rating(answers, "exception_rate"))
    quality_after = min(100, round(quality_before + (100 - quality_before) * coverage))

    csat_before = _to_100(6 - _rating(answers, "human_judgment_frequency"))
    csat_after = min(100, round(csat_before + (100 - csat_before) * coverage))

    rows = [
        {"kpi": "Cycle Time (manual-effort index)", "before": cycle_time_before, "after": cycle_time_after, "unit": "index"},
        {"kpi": "Quality Index", "before": quality_before, "after": quality_after, "unit": "index"},
        {"kpi": "Compliance Rate", "before": compliance_before, "after": compliance_after, "unit": "%"},
        {"kpi": "Error Rate", "before": error_before, "after": error_after, "unit": "%"},
        {"kpi": "Customer Satisfaction Index", "before": csat_before, "after": csat_after, "unit": "index"},
    ]
    if roi is not None:
        rows.insert(
            1,
            {
                "kpi": f"Annual Cost ({roi['currency']})",
                "before": roi["current_annual_cost"],
                "after": roi["post_automation_cost"],
                "unit": roi["currency"],
            },
        )

    objectives_selected = len(_multi(answers, "business_objectives"))
    business_value_score = min(100, 40 + objectives_selected * 10)
    payback = roi.get("payback_months") if roi else None
    if payback is not None:
        if payback <= 6:
            business_value_score = min(100, business_value_score + 15)
        elif payback <= 12:
            business_value_score = min(100, business_value_score + 8)

    return {
        "rows": rows,
        "business_value_score": business_value_score,
    }


def _final_recommendation(
    process_dna: dict,
    decision_complexity: dict,
    ai_readiness: dict,
    business_case: dict,
    answers: dict,
    recommendation: str,
) -> dict:
    raw = process_dna["raw"]
    process_dna_score = round(raw["Rule Based"] * 0.4 + (100 - raw["Creativity"]) * 0.3 + (100 - raw["Collaboration"]) * 0.3)

    governance_avg = _rating(answers, "ai_governance_maturity") * 0.6 + (6 - _rating(answers, "compliance_criticality")) * 0.4
    governance_readiness = _to_100(governance_avg)

    change_avg = (_rating(answers, "automation_landscape") + _rating(answers, "ai_skills_readiness")) / 2
    change_readiness = _to_100(change_avg)

    dimensions = [
        {"name": "Process DNA", "score": process_dna_score, "weight": 20},
        {"name": "AI Readiness", "score": ai_readiness["ai_readiness_pct"], "weight": 20},
        {"name": "Decision Complexity", "score": decision_complexity["complexity_score"], "weight": 20},
        {"name": "Business Value", "score": business_case["business_value_score"], "weight": 20},
        {"name": "Governance Readiness", "score": governance_readiness, "weight": 10},
        {"name": "Change Readiness", "score": change_readiness, "weight": 10},
    ]
    weighted_total = round(sum(d["score"] * d["weight"] / 100 for d in dimensions))

    strategy_map = {
        "Manual Process": "Standardize the process before automating",
        "RPA": "Traditional RPA",
        "RPA + Native UiPath AI": "RPA + UiPath AI",
        "RPA + External AI": "External AI",
    }

    return {
        "dimensions": dimensions,
        "weighted_total": weighted_total,
        "strategy": strategy_map.get(recommendation, recommendation),
        "recommendation": recommendation,
    }


def compute_final_scorecard(
    *,
    answers: dict,
    category: str,
    recommendation: str,
    matched_use_case: str | None,
    automation_maturity_score: float,
    roi: dict | None = None,
) -> dict:
    business_objectives = _business_objectives(answers)
    process_dna = _process_dna(answers)
    decision_complexity = _decision_complexity(answers)
    ai_readiness = _ai_readiness(answers)
    heatmap = _automation_heatmap(process_dna, decision_complexity)
    value_proposition = _value_proposition(business_objectives, matched_use_case)
    business_case = _business_case(answers, category, automation_maturity_score, roi)
    final_recommendation = _final_recommendation(
        process_dna, decision_complexity, ai_readiness, business_case, answers, recommendation
    )

    return {
        "business_objective": business_objectives,
        "process_dna": process_dna,
        "decision_complexity": decision_complexity,
        "ai_readiness": ai_readiness,
        "automation_heatmap": heatmap,
        "value_proposition": value_proposition,
        "business_case": business_case,
        "final_recommendation": final_recommendation,
    }
