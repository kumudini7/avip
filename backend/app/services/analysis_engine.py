from __future__ import annotations

from textwrap import shorten
from typing import Any

from app.models.document import ProcessDocument
from app.models.project import Project
from app.services.analysis_scoring import score_analysis
from app.services.ai_providers import build_provider


def _build_prompt(project: Project, documents: list[ProcessDocument], text: str) -> str:
    document_lines = []
    for document in documents[:5]:
        preview = shorten(document.extracted_text or "", width=1800, placeholder=" ...")
        document_lines.append(
            f"- File: {document.original_filename}\n"
            f"  Preview: {preview}\n"
        )

    return f"""
You are analyzing a business process for intelligent automation opportunities.
Return JSON only with the following keys:
- summary: concise executive summary
- steps: array of objects with step, recommendation, rationale, confidence
- recommendations: object with automation_stack, vendor_stack, human_review_policy
- risks: array of risk statements
- mitigations: array of mitigation statements
- kpi_mapping: array of KPI names
- benchmark: object with automation, roi, payback when available
- confidence: integer from 0 to 100

Project:
- Name: {project.name}
- Client: {project.client_name or "Not provided"}
- Industry: {project.industry or "Not provided"}
- Description: {project.description or "Not provided"}

Document previews:
{chr(10).join(document_lines) if document_lines else "- No uploaded documents"}

Combined source text:
{text[:12000]}
""".strip()


def analyze_process(project: Project, documents: list[ProcessDocument]) -> dict[str, Any]:
    combined_text = "\n\n".join(
        part
        for part in [project.description or "", *[doc.extracted_text or "" for doc in documents]]
        if part
    )
    provider = build_provider()
    prompt = _build_prompt(project, documents, combined_text)

    insights: dict[str, Any] = {}
    try:
        insights = provider.analyze(prompt)
    except Exception:
        insights = {}

    analysis = score_analysis(combined_text, documents, project, insights=insights)
    analysis["analysis_provider"] = insights.get("_provider", getattr(provider, "name", "rule-based"))
    analysis["analysis_model"] = insights.get("_model")
    if insights:
        analysis["analysis_mode"] = "ai"
    elif analysis["analysis_provider"] == "rule-based":
        analysis["analysis_mode"] = "deterministic"
    else:
        analysis["analysis_mode"] = "fallback"
    return analysis
