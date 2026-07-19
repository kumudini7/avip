from __future__ import annotations

import json
import re
from typing import Any, Callable

from app.core.config import settings

try:
    from openai import AzureOpenAI, OpenAI
except Exception:  # pragma: no cover - optional import guard
    AzureOpenAI = None
    OpenAI = None

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional import guard
    genai = None

try:
    from anthropic import Anthropic
except Exception:  # pragma: no cover - optional import guard
    Anthropic = None


class GtmContentGenerationError(RuntimeError):
    pass


class ProviderUnavailable(RuntimeError):
    pass


GENERATION_TIMEOUT_SECONDS = 30
TEMPERATURE = 0.4


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


# --- Generic provider chain (used by both stage and pitch generation) ------


def _call_openai(system_prompt: str, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    if OpenAI is None or not settings.openai_api_key:
        raise ProviderUnavailable("OpenAI is not configured")

    client = OpenAI(api_key=settings.openai_api_key, timeout=GENERATION_TIMEOUT_SECONDS, max_retries=1)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=TEMPERATURE,
        response_format={"type": "json_object"},
    )
    payload = _extract_json(response.choices[0].message.content or "{}")
    payload["_model"] = f"openai:{settings.openai_model}"
    return payload


def _call_groq(system_prompt: str, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    if OpenAI is None or not settings.groq_api_key:
        raise ProviderUnavailable("Groq is not configured")

    client = OpenAI(
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
        timeout=GENERATION_TIMEOUT_SECONDS,
        max_retries=1,
    )
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=TEMPERATURE,
        response_format={"type": "json_object"},
    )
    payload = _extract_json(response.choices[0].message.content or "{}")
    payload["_model"] = f"groq:{settings.groq_model}"
    return payload


def _call_gemini(system_prompt: str, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    if genai is None or not settings.gemini_api_key:
        raise ProviderUnavailable("Gemini is not configured")

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    response = model.generate_content(
        f"{system_prompt}\n\n{prompt}",
        generation_config={"temperature": TEMPERATURE, "response_mime_type": "application/json"},
        request_options={"timeout": GENERATION_TIMEOUT_SECONDS},
    )
    payload = _extract_json(getattr(response, "text", "") or "")
    payload["_model"] = f"gemini:{settings.gemini_model}"
    return payload


def _call_anthropic(system_prompt: str, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    if Anthropic is None or not settings.anthropic_api_key:
        raise ProviderUnavailable("Anthropic is not configured")

    client = Anthropic(api_key=settings.anthropic_api_key, timeout=GENERATION_TIMEOUT_SECONDS, max_retries=1)
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    text = next((block.text for block in response.content if block.type == "text"), "{}")
    payload = json.loads(text)
    payload["_model"] = f"anthropic:{settings.anthropic_model}"
    return payload


def _call_azure_openai(system_prompt: str, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
    if AzureOpenAI is None or not settings.azure_openai_api_key or not settings.azure_openai_endpoint:
        raise ProviderUnavailable("Azure OpenAI is not configured")

    deployment = settings.azure_openai_deployment or settings.azure_openai_model
    client = AzureOpenAI(
        api_key=settings.azure_openai_api_key,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
        timeout=GENERATION_TIMEOUT_SECONDS,
        max_retries=1,
    )
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=TEMPERATURE,
        response_format={"type": "json_object"},
    )
    payload = _extract_json(response.choices[0].message.content or "{}")
    payload["_model"] = f"azure-openai:{deployment}"
    return payload


PROVIDER_CHAIN: list[tuple[str, Callable[[str, str, dict[str, Any]], dict[str, Any]]]] = [
    ("openai", _call_openai),
    ("groq", _call_groq),
    ("gemini", _call_gemini),
    ("anthropic", _call_anthropic),
    ("azure-openai", _call_azure_openai),
]


def _run_provider_chain(
    *,
    system_prompt: str,
    prompt: str,
    schema: dict[str, Any],
    validate: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    failures: list[str] = []
    for provider_name, call in PROVIDER_CHAIN:
        try:
            payload = call(system_prompt, prompt, schema)
        except ProviderUnavailable as exc:
            failures.append(f"{provider_name}: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001 - try the next provider on any failure
            failures.append(f"{provider_name}: {exc}")
            continue

        if validate(payload):
            return payload
        failures.append(f"{provider_name}: response was missing required fields")

    raise GtmContentGenerationError(
        "All AI providers failed to generate content. " + " | ".join(failures)
    )


# --- Stage playbook generation ----------------------------------------------

STAGE_SYSTEM_PROMPT = (
    "You are a senior GTM consultant at Jade Global's Agentic AI practice. "
    "You write consulting playbook content for a specific client engagement and GTM stage. "
    "Always respond with strict JSON matching the requested schema. No markdown, no commentary."
)

STAGE_REQUIRED_FIELDS = {"objective", "client_value", "approach", "tools", "pitch_line", "checklist"}

STAGE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "objective": {"type": "string"},
        "client_value": {"type": "string"},
        "approach": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step": {"type": "string"},
                    "detail": {"type": "string"},
                },
                "required": ["step", "detail"],
                "additionalProperties": False,
            },
        },
        "tools": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["name", "description"],
                "additionalProperties": False,
            },
        },
        "pitch_line": {"type": "string"},
        "checklist": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["objective", "client_value", "approach", "tools", "pitch_line", "checklist"],
    "additionalProperties": False,
}


def _validate_stage_payload(payload: dict[str, Any]) -> bool:
    if not STAGE_REQUIRED_FIELDS.issubset(payload.keys()):
        return False
    checklist = payload.get("checklist")
    return isinstance(checklist, list) and len(checklist) > 0


def _build_stage_prompt(
    *,
    client_name: str,
    industry: str,
    stage_label: str,
    kpis: list[dict[str, Any]],
    existing_notes: str | None,
) -> str:
    kpi_lines = (
        "\n".join(f"- {kpi['label']}: baseline {kpi['baseline_value']} -> target {kpi['target_value']}" for kpi in kpis)
        if kpis
        else "None logged yet."
    )
    notes_block = existing_notes.strip() if existing_notes and existing_notes.strip() else "None yet."

    return f"""Generate GTM playbook content for the "{stage_label}" stage of an Agentic AI engagement.

Client: {client_name}
Industry: {industry}
KPIs already tracked for this engagement:
{kpi_lines}
Consultant notes captured so far for this stage:
{notes_block}

Tailor every field specifically to this client and industry - do not write generic automation copy.

Return JSON with exactly this shape:
{{
  "objective": "1-2 sentence objective for this stage, specific to {client_name} in {industry}",
  "client_value": "1-2 sentence statement of the value this stage delivers to {client_name}",
  "approach": [
    {{"step": "short step title", "detail": "2-3 sentence guidance on how to actually execute this step for {client_name}"}}
    // exactly 4 items
  ],
  "tools": [
    {{"name": "tool or technique name", "description": "1 sentence on what it is and when to use it in this stage"}}
    // exactly 4 items
  ],
  "pitch_line": "a single quotable sentence a consultant could say to {client_name} to sell the value of this stage",
  "checklist": [
    "short actionable checklist item specific to {client_name}'s {stage_label} stage"
    // 4 to 6 items
  ]
}}"""


def generate_stage_content(
    *,
    client_name: str,
    industry: str,
    stage_label: str,
    kpis: list[dict[str, Any]],
    existing_notes: str | None,
) -> dict[str, Any]:
    prompt = _build_stage_prompt(
        client_name=client_name,
        industry=industry,
        stage_label=stage_label,
        kpis=kpis,
        existing_notes=existing_notes,
    )
    return _run_provider_chain(
        system_prompt=STAGE_SYSTEM_PROMPT,
        prompt=prompt,
        schema=STAGE_OUTPUT_SCHEMA,
        validate=_validate_stage_payload,
    )


# --- Pitch builder generation ------------------------------------------------

PITCH_SYSTEM_PROMPT = (
    "You are a senior GTM consultant at Jade Global's Agentic AI practice, helping a colleague build a client pitch. "
    "You write as-is/to-be workflow analysis and KPI targets for a prospective client based on their industry and "
    "stated pain points. Always respond with strict JSON matching the requested schema. No markdown, no commentary."
)

PITCH_REQUIRED_FIELDS = {"as_is", "to_be", "kpi_template"}

PITCH_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "as_is": {"type": "array", "items": {"type": "string"}},
        "to_be": {"type": "array", "items": {"type": "string"}},
        "kpi_template": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "kpi": {"type": "string"},
                    "baseline": {"type": "string"},
                    "target": {"type": "string"},
                },
                "required": ["kpi", "baseline", "target"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["as_is", "to_be", "kpi_template"],
    "additionalProperties": False,
}


def _validate_pitch_payload(payload: dict[str, Any]) -> bool:
    if not PITCH_REQUIRED_FIELDS.issubset(payload.keys()):
        return False
    return (
        isinstance(payload.get("as_is"), list)
        and len(payload["as_is"]) > 0
        and isinstance(payload.get("to_be"), list)
        and len(payload["to_be"]) > 0
        and isinstance(payload.get("kpi_template"), list)
        and len(payload["kpi_template"]) > 0
    )


def _build_pitch_prompt(*, industry: str, pain_points: list[str]) -> str:
    pain_point_lines = "\n".join(f"- {point}" for point in pain_points)

    return f"""Generate pitch content for a prospective client in the "{industry}" industry.

Stated pain points:
{pain_point_lines}

Tailor every field specifically to these pain points - do not write generic automation copy.

Return JSON with exactly this shape:
{{
  "as_is": [
    "short description of one current-state workflow step, addressing the stated pain points"
    // exactly 4 items, in sequence
  ],
  "to_be": [
    "short description of one future-state workflow step with an agentic AI layer, addressing the stated pain points"
    // exactly 4 items, in sequence, same scope as as_is
  ],
  "kpi_template": [
    {{"kpi": "KPI name relevant to the stated pain points", "baseline": "current baseline value", "target": "target value after agentic AI adoption"}}
    // exactly 3 items
  ]
}}"""


def generate_pitch_content(*, industry: str, pain_points: list[str]) -> dict[str, Any]:
    prompt = _build_pitch_prompt(industry=industry, pain_points=pain_points)
    return _run_provider_chain(
        system_prompt=PITCH_SYSTEM_PROMPT,
        prompt=prompt,
        schema=PITCH_OUTPUT_SCHEMA,
        validate=_validate_pitch_payload,
    )
