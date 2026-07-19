"""Deterministic readiness scoring: turns the 10 hardcoded questionnaire answers
(1-5 each) into 3 headline scores, a 4-tier recommendation, business-justification
bullets, and a high-level ROI estimate. Runs with zero external/API dependency so
it always works, independent of whether Claude is configured.
"""

from __future__ import annotations

from app.data.questionnaire import get_questionnaire

RECOMMENDATION_MANUAL = "Manual Process"
RECOMMENDATION_RPA = "RPA"
RECOMMENDATION_RPA_NATIVE_AI = "RPA + Native UiPath AI"
RECOMMENDATION_RPA_EXTERNAL_AI = "RPA + External AI"

_DEFAULT_ANSWER = 3


def _inv(value: int) -> int:
    return 6 - value


def _to_100(weighted_avg: float) -> int:
    return round((weighted_avg - 1) / 4 * 100)


def _get(answers: dict[str, int], key: str) -> int:
    value = answers.get(key, _DEFAULT_ANSWER)
    try:
        value = int(value)
    except (TypeError, ValueError):
        return _DEFAULT_ANSWER
    return min(5, max(1, value))


def _determine_recommendation(
    *,
    process_standardization: int,
    human_judgment_frequency: int,
    data_type: int,
    ai_governance_maturity: int,
    compliance_criticality: int,
    automation_maturity_score: int,
) -> str:
    if automation_maturity_score < 30 and process_standardization <= 2:
        return RECOMMENDATION_MANUAL
    if data_type <= 2 and human_judgment_frequency <= 2:
        return RECOMMENDATION_RPA
    if (
        data_type >= 4
        and human_judgment_frequency >= 4
        and ai_governance_maturity >= 3
        and compliance_criticality <= 3
    ):
        return RECOMMENDATION_RPA_EXTERNAL_AI
    return RECOMMENDATION_RPA_NATIVE_AI


_ROI_ESTIMATES = {
    RECOMMENDATION_MANUAL: "Not yet recommended for automation - standardize the process first, then reassess.",
    RECOMMENDATION_RPA: "Typically 60-85% of the process automated, with payback in 6-10 months.",
    RECOMMENDATION_RPA_NATIVE_AI: "Typically 55-80% of the process automated, with payback in 10-14 months.",
    RECOMMENDATION_RPA_EXTERNAL_AI: "Typically 50-75% of the process automated, with payback in 12-16 months given added integration complexity.",
}


def _label_for(domain: str, key: str, value: int) -> str:
    for question in get_questionnaire(domain):
        if question["key"] == key:
            return question["scale_labels"].get(value, str(value))
    return str(value)


def _build_justification(domain: str, answers: dict[str, int], recommendation: str) -> list[str]:
    bullets: list[str] = []

    standardization = _get(answers, "process_standardization")
    judgment = _get(answers, "human_judgment_frequency")
    data_type = _get(answers, "data_type")
    exceptions = _get(answers, "exception_rate")
    governance = _get(answers, "ai_governance_maturity")

    bullets.append(
        f"Process standardization ({standardization}/5): {_label_for(domain, 'process_standardization', standardization)}"
    )
    bullets.append(
        f"Human judgment required ({judgment}/5): {_label_for(domain, 'human_judgment_frequency', judgment)}"
    )
    bullets.append(
        f"Data type ({data_type}/5): {_label_for(domain, 'data_type', data_type)}"
    )

    if recommendation == RECOMMENDATION_MANUAL:
        bullets.append("The process is too undefined to automate reliably today - document and standardize it before revisiting automation.")
    elif recommendation == RECOMMENDATION_RPA:
        bullets.append("Structured data and low judgment requirements make this a strong fit for deterministic, rule-based RPA.")
    elif recommendation == RECOMMENDATION_RPA_EXTERNAL_AI:
        bullets.append(
            f"AI governance maturity ({governance}/5) supports responsible use of external/generative AI for the unstructured, judgment-heavy parts of this process."
        )
    else:
        bullets.append(
            f"Exception rate ({exceptions}/5): {_label_for(domain, 'exception_rate', exceptions)} - UiPath's native AI (Document Understanding, AI Center) can handle this without sending data outside your environment."
        )

    return bullets


def compute_scores(*, domain: str, answers: dict[str, int]) -> dict:
    process_standardization = _get(answers, "process_standardization")
    human_judgment_frequency = _get(answers, "human_judgment_frequency")
    data_type = _get(answers, "data_type")
    rule_change_frequency = _get(answers, "rule_change_frequency")
    exception_rate = _get(answers, "exception_rate")
    automation_landscape = _get(answers, "automation_landscape")
    ai_governance_maturity = _get(answers, "ai_governance_maturity")
    compliance_criticality = _get(answers, "compliance_criticality")
    system_integration_complexity = _get(answers, "system_integration_complexity")

    ai_readiness_avg = (
        ai_governance_maturity * 0.35
        + automation_landscape * 0.25
        + data_type * 0.20
        + human_judgment_frequency * 0.20
    )
    automation_maturity_avg = (
        process_standardization * 0.35
        + automation_landscape * 0.35
        + _inv(human_judgment_frequency) * 0.15
        + _inv(exception_rate) * 0.15
    )
    migration_readiness_avg = (
        process_standardization * 0.25
        + _inv(rule_change_frequency) * 0.20
        + _inv(exception_rate) * 0.20
        + _inv(system_integration_complexity) * 0.20
        + _inv(compliance_criticality) * 0.15
    )

    ai_readiness_score = _to_100(ai_readiness_avg)
    automation_maturity_score = _to_100(automation_maturity_avg)
    migration_readiness_score = _to_100(migration_readiness_avg)

    recommendation = _determine_recommendation(
        process_standardization=process_standardization,
        human_judgment_frequency=human_judgment_frequency,
        data_type=data_type,
        ai_governance_maturity=ai_governance_maturity,
        compliance_criticality=compliance_criticality,
        automation_maturity_score=automation_maturity_score,
    )

    normalized_answers = {
        "process_standardization": process_standardization,
        "human_judgment_frequency": human_judgment_frequency,
        "data_type": data_type,
        "rule_change_frequency": rule_change_frequency,
        "exception_rate": exception_rate,
        "automation_landscape": automation_landscape,
        "ai_governance_maturity": ai_governance_maturity,
        "compliance_criticality": compliance_criticality,
        "system_integration_complexity": system_integration_complexity,
    }

    return {
        "ai_readiness_score": ai_readiness_score,
        "automation_maturity_score": automation_maturity_score,
        "migration_readiness_score": migration_readiness_score,
        "recommendation": recommendation,
        "business_justification": _build_justification(domain, normalized_answers, recommendation),
        "roi_estimate": _ROI_ESTIMATES[recommendation],
    }
