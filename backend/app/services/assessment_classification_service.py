from __future__ import annotations

import json
import re
from typing import Any

from app.core.config import settings
from app.data.use_cases import get_use_cases_for_domain

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional import guard
    OpenAI = None


class ClassificationError(RuntimeError):
    pass


GENERATION_TIMEOUT_SECONDS = 45

SYSTEM_PROMPT = (
    "You are a UiPath automation expert. Classify the process based on the assessment answers. "
    "Return ONLY valid JSON, no markdown."
)

REQUIRED_FIELDS = {
    "category",
    "matched_use_case",
    "confidence_score",
    "reasoning",
    "similar_use_cases",
    "complexity",
    "estimated_timeline",
}

VALID_CATEGORIES = {"pure_rpa", "rpa_ai", "rpa_ui"}
VALID_COMPLEXITY = {"low", "medium", "high"}


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = (text or "").strip()
    if not cleaned:
        return {}
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return {}
    return {}


def _validate_payload(payload: dict[str, Any]) -> bool:
    if not REQUIRED_FIELDS.issubset(payload.keys()):
        return False
    if payload.get("category") not in VALID_CATEGORIES:
        return False
    if payload.get("complexity") not in VALID_COMPLEXITY:
        return False
    if not isinstance(payload.get("reasoning"), list) or not payload["reasoning"]:
        return False
    if not isinstance(payload.get("similar_use_cases"), list):
        return False
    return True


def _format_answer(question: dict[str, Any], value: Any) -> str:
    if value is None:
        return "(not answered)"
    question_type = question.get("question_type", "rating")
    if question_type == "percent":
        return f"{value}%"
    if question_type == "multi_select":
        if not isinstance(value, list) or not value:
            return "(not answered)"
        options_by_key = {option["key"]: option["label"] for option in question.get("options") or []}
        return ", ".join(options_by_key.get(item, item) for item in value)
    label = question["scale_labels"].get(value, "(not answered)")
    return f"{value}/5 - {label}"


def _build_prompt(
    *,
    domain: str,
    business_context: dict[str, Any],
    questions: list[dict[str, Any]],
    responses_by_question: dict[str, Any],
) -> str:
    context_lines = "\n".join(f"- {key}: {value}" for key, value in business_context.items())

    qa_lines = []
    for question in questions:
        value = responses_by_question.get(question["key"])
        answer_text = _format_answer(question, value)
        qa_lines.append(f"- Q: {question['question_text']}\n  A: {answer_text}")
    qa_block = "\n".join(qa_lines) if qa_lines else "No questionnaire answers provided."

    kb_entries = get_use_cases_for_domain(domain)
    kb_lines = []
    for entry in kb_entries:
        kb_lines.append(
            f"- [{entry['category']}] {entry['title']}: {entry['overview']} "
            f"(systems: {', '.join(entry['systems_involved'])}; complexity: {entry['complexity']})"
        )
    kb_block = "\n".join(kb_lines)

    return f"""Domain selected: {domain}

Business context:
{context_lines}

Questionnaire answers:
{qa_block}

Use-case knowledge base for this domain:
{kb_block}

Classify this process against the knowledge base above. Return JSON with exactly this shape:
{{
  "category": "pure_rpa" | "rpa_ai" | "rpa_ui",
  "matched_use_case": "the single best-matching use case title from the knowledge base above",
  "confidence_score": <integer 0-100>,
  "reasoning": ["short reason 1", "short reason 2", "short reason 3", "short reason 4"],
  "similar_use_cases": ["other use case title 1", "other use case title 2"],
  "complexity": "low" | "medium" | "high",
  "estimated_timeline": "e.g. 8-12 weeks"
}}"""


def _call_groq(prompt: str) -> dict[str, Any]:
    if OpenAI is None or not settings.groq_api_key:
        raise ClassificationError("Groq is not configured (missing GROQ_API_KEY)")

    client = OpenAI(
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
        timeout=GENERATION_TIMEOUT_SECONDS,
        max_retries=1,
    )
    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
    except Exception as exc:  # noqa: BLE001 - surfaced as a clean 502 at the router boundary
        raise ClassificationError(f"Groq API call failed: {exc}") from exc

    text = response.choices[0].message.content or "{}"
    payload = _extract_json(text)
    if not _validate_payload(payload):
        raise ClassificationError("Groq response was missing required fields")
    return payload


def classify_assessment(
    *,
    domain: str,
    business_context: dict[str, Any],
    questions: list[dict[str, Any]],
    responses_by_question: dict[str, Any],
) -> dict[str, Any]:
    prompt = _build_prompt(
        domain=domain,
        business_context=business_context,
        questions=questions,
        responses_by_question=responses_by_question,
    )
    return _call_groq(prompt)
